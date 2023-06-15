#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
from __future__ import annotations

import copy
import logging
import uuid
from datetime import date, datetime, timedelta
from functools import partial
from typing import Any, NamedTuple
from unittest import mock

import jinja2
import pytest

from airflow.decorators import task as task_decorator
from airflow.exceptions import AirflowException, DagInvalidTriggerRule, RemovedInAirflow3Warning
from airflow.lineage.entities import File
from airflow.models import DAG
from airflow.models.baseoperator import BaseOperator, BaseOperatorMeta, chain, cross_downstream
from airflow.utils.context import Context
from airflow.utils.edgemodifier import Label
from airflow.utils.task_group import TaskGroup
from airflow.utils.trigger_rule import TriggerRule
from airflow.utils.weight_rule import WeightRule
from tests.models import DEFAULT_DATE
from tests.test_utils.config import conf_vars
from tests.test_utils.mock_operators import DeprecatedOperator, MockOperator


def tasks_to_clear(dag, task, upstream):
    return set(
        dag.partial_subset(
            task_ids_or_regex=[task.task_id], include_downstream=not upstream, include_upstream=upstream
        ).tasks
    )


class ClassWithCustomAttributes:
    """Class for testing purpose: allows to create objects with custom attributes in one single statement."""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self):
        return f"{ClassWithCustomAttributes.__name__}({str(self.__dict__)})"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)


# Objects with circular references (for testing purpose)
object1 = ClassWithCustomAttributes(attr="{{ foo }}_1", template_fields=["ref"])
object2 = ClassWithCustomAttributes(attr="{{ foo }}_2", ref=object1, template_fields=["ref"])
setattr(object1, "ref", object2)


# Essentially similar to airflow.models.baseoperator.BaseOperator
class DummyClass(metaclass=BaseOperatorMeta):
    def __init__(self, test_param, params=None, default_args=None):
        self.test_param = test_param

    def set_xcomargs_dependencies(self):
        ...


class DummySubClass(DummyClass):
    def __init__(self, test_sub_param, **kwargs):
        super().__init__(**kwargs)
        self.test_sub_param = test_sub_param


class MockNamedTuple(NamedTuple):
    var1: str
    var2: str


class TestBaseOperator:
    def test_expand(self):
        dummy = DummyClass(test_param=True)
        assert dummy.test_param

        with pytest.raises(AirflowException, match="missing keyword argument 'test_param'"):
            DummySubClass(test_sub_param=True)

    def test_default_args(self):
        default_args = {"test_param": True}
        dummy_class = DummyClass(default_args=default_args)
        assert dummy_class.test_param

        default_args = {"test_param": True, "test_sub_param": True}
        dummy_subclass = DummySubClass(default_args=default_args)
        assert dummy_class.test_param
        assert dummy_subclass.test_sub_param

        default_args = {"test_param": True}
        dummy_subclass = DummySubClass(default_args=default_args, test_sub_param=True)
        assert dummy_class.test_param
        assert dummy_subclass.test_sub_param

        with pytest.raises(AirflowException, match="missing keyword argument 'test_sub_param'"):
            DummySubClass(default_args=default_args)

    def test_execution_timeout_type(self):
        with pytest.raises(
            ValueError, match="execution_timeout must be timedelta object but passed as type: <class 'str'>"
        ):
            BaseOperator(task_id="test", execution_timeout="1")

        with pytest.raises(
            ValueError, match="execution_timeout must be timedelta object but passed as type: <class 'int'>"
        ):
            BaseOperator(task_id="test", execution_timeout=1)

    def test_incorrect_default_args(self):
        default_args = {"test_param": True, "extra_param": True}
        dummy_class = DummyClass(default_args=default_args)
        assert dummy_class.test_param

        default_args = {"random_params": True}
        with pytest.raises(AirflowException, match="missing keyword argument 'test_param'"):
            DummyClass(default_args=default_args)

    def test_incorrect_priority_weight(self):
        error_msg = "`priority_weight` for task 'test_op' only accepts integers, received '<class 'str'>'."
        with pytest.raises(AirflowException, match=error_msg):
            BaseOperator(task_id="test_op", priority_weight="2")

    def test_illegal_args(self):
        """
        Tests that Operators reject illegal arguments
        """
        msg = r"Invalid arguments were passed to BaseOperator \(task_id: test_illegal_args\)"
        with conf_vars({("operators", "allow_illegal_arguments"): "True"}):
            with pytest.warns(RemovedInAirflow3Warning, match=msg):
                BaseOperator(
                    task_id="test_illegal_args",
                    illegal_argument_1234="hello?",
                )

    def test_illegal_args_forbidden(self):
        """
        Tests that operators raise exceptions on illegal arguments when
        illegal arguments are not allowed.
        """
        msg = r"Invalid arguments were passed to BaseOperator \(task_id: test_illegal_args\)"
        with pytest.raises(AirflowException, match=msg):
            BaseOperator(
                task_id="test_illegal_args",
                illegal_argument_1234="hello?",
            )

    def test_trigger_rule_validation(self):
        from airflow.models.abstractoperator import DEFAULT_TRIGGER_RULE

        fail_stop_dag = DAG(
            dag_id="test_dag_trigger_rule_validation", start_date=DEFAULT_DATE, fail_stop=True
        )
        non_fail_stop_dag = DAG(
            dag_id="test_dag_trigger_rule_validation", start_date=DEFAULT_DATE, fail_stop=False
        )

        # An operator with default trigger rule and a fail-stop dag should be allowed
        try:
            BaseOperator(
                task_id="test_valid_trigger_rule", dag=fail_stop_dag, trigger_rule=DEFAULT_TRIGGER_RULE
            )
        except DagInvalidTriggerRule as exception:
            assert (
                False
            ), f"BaseOperator raises exception with fail-stop dag & default trigger rule: {exception}"

        # An operator with non default trigger rule and a non fail-stop dag should be allowed
        try:
            BaseOperator(
                task_id="test_valid_trigger_rule", dag=non_fail_stop_dag, trigger_rule=TriggerRule.DUMMY
            )
        except DagInvalidTriggerRule as exception:
            assert (
                False
            ), f"BaseOperator raises exception with non fail-stop dag & non-default trigger rule: {exception}"

        # An operator with non default trigger rule and a fail stop dag should not be allowed
        with pytest.raises(DagInvalidTriggerRule):
            BaseOperator(
                task_id="test_invalid_trigger_rule", dag=fail_stop_dag, trigger_rule=TriggerRule.DUMMY
            )

    @pytest.mark.parametrize(
        ("content", "context", "expected_output"),
        [
            ("{{ foo }}", {"foo": "bar"}, "bar"),
            (["{{ foo }}_1", "{{ foo }}_2"], {"foo": "bar"}, ["bar_1", "bar_2"]),
            (("{{ foo }}_1", "{{ foo }}_2"), {"foo": "bar"}, ("bar_1", "bar_2")),
            (
                {"key1": "{{ foo }}_1", "key2": "{{ foo }}_2"},
                {"foo": "bar"},
                {"key1": "bar_1", "key2": "bar_2"},
            ),
            (
                {"key_{{ foo }}_1": 1, "key_2": "{{ foo }}_2"},
                {"foo": "bar"},
                {"key_{{ foo }}_1": 1, "key_2": "bar_2"},
            ),
            (date(2018, 12, 6), {"foo": "bar"}, date(2018, 12, 6)),
            (datetime(2018, 12, 6, 10, 55), {"foo": "bar"}, datetime(2018, 12, 6, 10, 55)),
            (MockNamedTuple("{{ foo }}_1", "{{ foo }}_2"), {"foo": "bar"}, MockNamedTuple("bar_1", "bar_2")),
            ({"{{ foo }}_1", "{{ foo }}_2"}, {"foo": "bar"}, {"bar_1", "bar_2"}),
            (None, {}, None),
            ([], {}, []),
            ({}, {}, {}),
            (
                # check nested fields can be templated
                ClassWithCustomAttributes(att1="{{ foo }}_1", att2="{{ foo }}_2", template_fields=["att1"]),
                {"foo": "bar"},
                ClassWithCustomAttributes(att1="bar_1", att2="{{ foo }}_2", template_fields=["att1"]),
            ),
            (
                # check deep nested fields can be templated
                ClassWithCustomAttributes(
                    nested1=ClassWithCustomAttributes(
                        att1="{{ foo }}_1", att2="{{ foo }}_2", template_fields=["att1"]
                    ),
                    nested2=ClassWithCustomAttributes(
                        att3="{{ foo }}_3", att4="{{ foo }}_4", template_fields=["att3"]
                    ),
                    template_fields=["nested1"],
                ),
                {"foo": "bar"},
                ClassWithCustomAttributes(
                    nested1=ClassWithCustomAttributes(
                        att1="bar_1", att2="{{ foo }}_2", template_fields=["att1"]
                    ),
                    nested2=ClassWithCustomAttributes(
                        att3="{{ foo }}_3", att4="{{ foo }}_4", template_fields=["att3"]
                    ),
                    template_fields=["nested1"],
                ),
            ),
            (
                # check null value on nested template field
                ClassWithCustomAttributes(att1=None, template_fields=["att1"]),
                {},
                ClassWithCustomAttributes(att1=None, template_fields=["att1"]),
            ),
            (
                # check there is no RecursionError on circular references
                object1,
                {"foo": "bar"},
                object1,
            ),
            # By default, Jinja2 drops one (single) trailing newline
            ("{{ foo }}\n\n", {"foo": "bar"}, "bar\n"),
        ],
    )
    def test_render_template(self, content, context, expected_output):
        """Test render_template given various input types."""
        task = BaseOperator(task_id="op1")

        result = task.render_template(content, context)
        assert result == expected_output

    @pytest.mark.parametrize(
        ("content", "context", "expected_output"),
        [
            ("{{ foo }}", {"foo": "bar"}, "bar"),
            ("{{ foo }}", {"foo": ["bar1", "bar2"]}, ["bar1", "bar2"]),
            (["{{ foo }}", "{{ foo | length}}"], {"foo": ["bar1", "bar2"]}, [["bar1", "bar2"], 2]),
            (("{{ foo }}_1", "{{ foo }}_2"), {"foo": "bar"}, ("bar_1", "bar_2")),
            ("{{ ds }}", {"ds": date(2018, 12, 6)}, date(2018, 12, 6)),
            (datetime(2018, 12, 6, 10, 55), {"foo": "bar"}, datetime(2018, 12, 6, 10, 55)),
            ("{{ ds }}", {"ds": datetime(2018, 12, 6, 10, 55)}, datetime(2018, 12, 6, 10, 55)),
            (MockNamedTuple("{{ foo }}_1", "{{ foo }}_2"), {"foo": "bar"}, MockNamedTuple("bar_1", "bar_2")),
            (
                ("{{ foo }}", "{{ foo.isoformat() }}"),
                {"foo": datetime(2018, 12, 6, 10, 55)},
                (datetime(2018, 12, 6, 10, 55), "2018-12-06T10:55:00"),
            ),
            (None, {}, None),
            ([], {}, []),
            ({}, {}, {}),
        ],
    )
    def test_render_template_with_native_envs(self, content, context, expected_output):
        """Test render_template given various input types with Native Python types"""
        with DAG("test-dag", start_date=DEFAULT_DATE, render_template_as_native_obj=True):
            task = BaseOperator(task_id="op1")

        result = task.render_template(content, context)
        assert result == expected_output

    def test_mapped_dag_slas_disabled_classic(self):
        with pytest.raises(AirflowException, match="SLAs are unsupported with mapped tasks"):
            with DAG(
                "test-dag", start_date=DEFAULT_DATE, default_args=dict(sla=timedelta(minutes=30))
            ) as dag:

                @dag.task
                def get_values():
                    return [0, 1, 2]

                task1 = get_values()

                class MyOp(BaseOperator):
                    def __init__(self, x, **kwargs):
                        self.x = x
                        super().__init__(**kwargs)

                    def execute(self, context):
                        print(self.x)

                MyOp.partial(task_id="hi").expand(x=task1)

    def test_mapped_dag_slas_disabled_taskflow(self):
        with pytest.raises(AirflowException, match="SLAs are unsupported with mapped tasks"):
            with DAG(
                "test-dag", start_date=DEFAULT_DATE, default_args=dict(sla=timedelta(minutes=30))
            ) as dag:

                @dag.task
                def get_values():
                    return [0, 1, 2]

                task1 = get_values()

                @dag.task
                def print_val(x):
                    print(x)

                print_val.expand(x=task1)

    def test_render_template_fields(self):
        """Verify if operator attributes are correctly templated."""
        task = MockOperator(task_id="op1", arg1="{{ foo }}", arg2="{{ bar }}")

        # Assert nothing is templated yet
        assert task.arg1 == "{{ foo }}"
        assert task.arg2 == "{{ bar }}"

        # Trigger templating and verify if attributes are templated correctly
        task.render_template_fields(context={"foo": "footemplated", "bar": "bartemplated"})
        assert task.arg1 == "footemplated"
        assert task.arg2 == "bartemplated"

    @pytest.mark.parametrize(("content",), [(object(),), (uuid.uuid4(),)])
    def test_render_template_fields_no_change(self, content):
        """Tests if non-templatable types remain unchanged."""
        task = BaseOperator(task_id="op1")

        result = task.render_template(content, {"foo": "bar"})
        assert content is result

    def test_nested_template_fields_declared_must_exist(self):
        """Test render_template when a nested template field is missing."""
        task = BaseOperator(task_id="op1")

        error_message = (
            "'missing_field' is configured as a template field but ClassWithCustomAttributes does not have "
            "this attribute."
        )
        with pytest.raises(AttributeError, match=error_message):
            task.render_template(
                ClassWithCustomAttributes(
                    template_fields=["missing_field"], task_type="ClassWithCustomAttributes"
                ),
                {},
            )

    def test_string_template_field_attr_is_converted_to_list(self):
        """Verify template_fields attribute is converted to a list if declared as a string."""

        class StringTemplateFieldsOperator(BaseOperator):
            template_fields = "a_string"

        warning_message = (
            "The `template_fields` value for StringTemplateFieldsOperator is a string but should be a "
            "list or tuple of string. Wrapping it in a list for execution. Please update "
            "StringTemplateFieldsOperator accordingly."
        )
        with pytest.warns(UserWarning, match=warning_message) as warnings:
            task = StringTemplateFieldsOperator(task_id="op1")

            assert len(warnings) == 1
            assert isinstance(task.template_fields, list)

    def test_jinja_invalid_expression_is_just_propagated(self):
        """Test render_template propagates Jinja invalid expression errors."""
        task = BaseOperator(task_id="op1")

        with pytest.raises(jinja2.exceptions.TemplateSyntaxError):
            task.render_template("{{ invalid expression }}", {})

    @mock.patch("airflow.templates.SandboxedEnvironment", autospec=True)
    def test_jinja_env_creation(self, mock_jinja_env):
        """Verify if a Jinja environment is created only once when templating."""
        task = MockOperator(task_id="op1", arg1="{{ foo }}", arg2="{{ bar }}")

        task.render_template_fields(context={"foo": "whatever", "bar": "whatever"})
        assert mock_jinja_env.call_count == 1

    def test_default_resources(self):
        task = BaseOperator(task_id="default-resources")
        assert task.resources is None

    def test_custom_resources(self):
        task = BaseOperator(task_id="custom-resources", resources={"cpus": 1, "ram": 1024})
        assert task.resources.cpus.qty == 1
        assert task.resources.ram.qty == 1024

    def test_default_email_on_actions(self):
        test_task = BaseOperator(task_id="test_default_email_on_actions")
        assert test_task.email_on_retry is True
        assert test_task.email_on_failure is True

    def test_email_on_actions(self):
        test_task = BaseOperator(
            task_id="test_default_email_on_actions", email_on_retry=False, email_on_failure=True
        )
        assert test_task.email_on_retry is False
        assert test_task.email_on_failure is True

    def test_get_flat_relative_ids_with_setup(self):
        dag = DAG(dag_id="test_dag", start_date=datetime.now())
        s1 = BaseOperator.as_setup(task_id="s1", dag=dag)
        w1 = BaseOperator(task_id="w1", dag=dag)
        w2 = BaseOperator(task_id="w2", dag=dag)
        w3 = BaseOperator(task_id="w3", dag=dag)
        t1 = BaseOperator.as_teardown(task_id="t1", dag=dag)

        s1 >> w1 >> w2 >> w3

        cleared_tasks = partial(tasks_to_clear, dag)

        # there is no teardown downstream of w2, so we assume w2 does not need s1
        assert set(w2.get_upstreams_only_setups_and_teardowns()) == set()

        w3 >> t1

        # now, w2 has a downstream teardown, but it's not connected directly to s1
        # (this is how we signal "this is the teardown for this setup")
        # so still, we don't regard s1 as a setup for w2
        assert set(w2.get_upstreams_only_setups_and_teardowns()) == set()

        s1 >> t1

        # now, we know that t1 is the teardown for s1, and it's downstream of
        # w2, so we can infer that w2 requires it, so now when we clear w2,
        # we will get s1 (because it's a setup for w2) and t1 (because
        # it is a teardown for s1)
        assert set(w2.get_upstreams_only_setups_and_teardowns()) == {s1, t1}
        assert w2.get_flat_relative_ids(upstream=True) == {"s1", "w1"}
        assert set(w2.get_upstreams_follow_setups()) == {s1, w1, t1}
        assert w2.get_flat_relative_ids(upstream=False) == {"w3", "t1"}
        assert w3.get_flat_relative_ids(upstream=False) == {"t1"}
        assert w1.get_flat_relative_ids(upstream=False) == {"w2", "w3", "t1"}
        assert set(w1.get_upstreams_only_setups_and_teardowns()) == {s1, t1}

        assert cleared_tasks(w3, upstream=False) == {s1, w3, t1}

    def test_get_flat_relative_ids_with_setup_nested_ctx_mgr(self):
        """Let's test some gnarlier cases here"""
        dag = DAG(dag_id="test_dag", start_date=datetime.now())
        s1 = BaseOperator.as_setup(task_id="s1", dag=dag)
        t1 = BaseOperator.as_teardown(task_id="t1", dag=dag)
        s2 = BaseOperator.as_setup(task_id="s2", dag=dag)
        t2 = BaseOperator.as_teardown(task_id="t2", dag=dag)
        with s1 >> t1:
            BaseOperator(task_id="w1", dag=dag)
            with s2 >> t2:
                BaseOperator(task_id="w2", dag=dag)
                BaseOperator(task_id="w3", dag=dag)
        # todo: implement tests

    def test_get_flat_relative_ids_with_setup_nested_no_ctx_mgr(self):
        """Let's test some gnarlier cases here"""
        dag = DAG(dag_id="test_dag", start_date=datetime.now())
        s1 = BaseOperator.as_setup(task_id="s1", dag=dag)
        t1 = BaseOperator.as_teardown(task_id="t1", dag=dag)
        s2 = BaseOperator.as_setup(task_id="s2", dag=dag)
        t2 = BaseOperator.as_teardown(task_id="t2", dag=dag)
        w1 = BaseOperator(task_id="w1", dag=dag)
        w2 = BaseOperator(task_id="w2", dag=dag)
        w3 = BaseOperator(task_id="w3", dag=dag)
        s1 >> t1
        s1 >> w1 >> t1
        s1 >> s2
        s2 >> t2
        s2 >> w2 >> w3 >> t2
        cleared_tasks = partial(tasks_to_clear, dag)

        assert w1.get_flat_relative_ids(upstream=True) == {"s1"}
        assert w1.get_flat_relative_ids(upstream=False) == {"t1"}
        assert cleared_tasks(w1, upstream=False) == {s1, w1, t1}
        assert cleared_tasks(w1, upstream=True) == {s1, w1, t1}
        assert w3.get_flat_relative_ids(upstream=True) == {"s1", "s2", "w2"}
        assert w3.get_flat_relative_ids(upstream=False) == {"t2"}
        assert cleared_tasks(w3, upstream=True) == {s1, t1, s2, w2, w3, t2}
        assert cleared_tasks(w3, upstream=False) == {s2, w3, t2}

    def test_get_flat_relative_ids_follows_teardowns(self):
        dag = DAG(dag_id="test_dag", start_date=datetime.now())
        s1 = BaseOperator.as_setup(task_id="s1", dag=dag)
        w1 = BaseOperator(task_id="w1", dag=dag)
        w2 = BaseOperator(task_id="w2", dag=dag)
        t1 = BaseOperator.as_teardown(task_id="t1", dag=dag)
        s1 >> w1 >> [w2, t1]
        s1 >> t1
        cleared_tasks = partial(tasks_to_clear, dag)

        # w2, we infer, does not require s1, since t1 does not come after it
        assert set(w2.get_upstreams_only_setups_and_teardowns()) == set()
        # w1, however, *does* require s1, since t1 is downstream of it
        assert set(w1.get_upstreams_only_setups_and_teardowns()) == {s1, t1}
        # downstream is just downstream and includes teardowns
        assert cleared_tasks(w1, upstream=False) == {s1, w1, w2, t1}
        assert cleared_tasks(w2, upstream=False) == {w2}
        # and if there's a downstream setup, it will be included as well
        s2 = BaseOperator.as_setup(task_id="s2", dag=dag)
        t1 >> s2
        assert w1.get_flat_relative_ids(upstream=False) == {"t1", "w2", "s2"}

    def test_get_flat_relative_ids_two_tasks_diff_setup_teardowns(self):
        with DAG(dag_id="test_dag", start_date=datetime.now()) as dag:
            s1 = BaseOperator.as_setup(task_id="s1")
            t1 = BaseOperator.as_teardown(task_id="t1")
            s2 = BaseOperator.as_setup(task_id="s2")
            t2 = BaseOperator.as_teardown(task_id="t2")
            w1 = BaseOperator(task_id="w1")
            w2 = BaseOperator(task_id="w2")
        s1 >> w1 >> [w2, t1]
        s1 >> t1
        s2 >> t2
        s2 >> w2 >> t2
        cleared_tasks = partial(tasks_to_clear, dag)

        assert set(w1.get_upstreams_only_setups_and_teardowns()) == {s1, t1}
        assert cleared_tasks(w1, upstream=False) == {s1, w1, t1, w2, t2}
        assert set(w2.get_upstreams_only_setups_and_teardowns()) == {s2, t2}
        assert cleared_tasks(w2, upstream=False) == {s2, w2, t2}

    def test_get_flat_relative_ids_one_task_multiple_setup_teardowns(self):
        with DAG(dag_id="test_dag", start_date=datetime.now()) as dag:
            s1a = BaseOperator.as_setup(task_id="s1a")
            s1b = BaseOperator.as_setup(task_id="s1b")
            t1 = BaseOperator.as_teardown(task_id="t1")
            s2 = BaseOperator.as_setup(task_id="s2")
            t2 = BaseOperator.as_teardown(task_id="t2")
            s3 = BaseOperator.as_setup(task_id="s3")
            t3a = BaseOperator.as_teardown(task_id="t3a")
            t3b = BaseOperator.as_teardown(task_id="t3b")
            w1 = BaseOperator(task_id="w1")
            w2 = BaseOperator(task_id="w2")
        # teardown t1 has two setups, s1a and s1b
        [s1a, s1b] >> t1
        # work 1 requires s1a and s1b, both of which are torn down by t1
        [s1a, s1b] >> w1 >> [w2, t1]

        # work 2 requires s2, and s3. s2 is torn down by t2. s3 is torn down by two teardowns, t3a and t3b.
        s2 >> t2
        s2 >> w2 >> t2
        s3 >> w2 >> [t3a, t3b]
        s3 >> [t3a, t3b]
        cleared_tasks = partial(tasks_to_clear, dag)
        assert set(w1.get_upstreams_only_setups_and_teardowns()) == {s1a, s1b, t1}
        assert cleared_tasks(w1, upstream=False) == {s1a, s1b, w1, t1, t3a, t3b, w2, t2}
        assert set(w2.get_upstreams_only_setups_and_teardowns()) == {s2, t2, s3, t3a, t3b}
        assert cleared_tasks(w2, upstream=False) == {s2, s3, w2, t2, t3a, t3b}

    def test_get_flat_relative_ids_with_setup_and_groups(self):
        """This is a dag with a setup / teardown at dag level and two task groups that have
        their own setups / teardowns.

        When we do tg >> dag_teardown, teardowns should be excluded from tg leaves.
        """
        dag = DAG(dag_id="test_dag", start_date=datetime.now())
        with dag:
            dag_setup = BaseOperator.as_setup(task_id="dag_setup")
            dag_teardown = BaseOperator.as_teardown(task_id="dag_teardown")
            dag_setup >> dag_teardown
            for group_name in ("g1", "g2"):
                with TaskGroup(group_name) as tg:
                    group_setup = BaseOperator.as_setup(task_id="group_setup")
                    w1 = BaseOperator(task_id="w1")
                    w2 = BaseOperator(task_id="w2")
                    w3 = BaseOperator(task_id="w3")
                    group_teardown = BaseOperator.as_teardown(task_id="group_teardown")
                    group_setup >> w1 >> w2 >> w3 >> group_teardown
                    group_setup >> group_teardown
                dag_setup >> tg >> dag_teardown
        g2_w2 = dag.task_dict["g2.w2"]

        # the line `dag_setup >> tg >> dag_teardown` should be equivalent to
        # dag_setup >> group_setup; w3 >> dag_teardown
        # i.e. not group_teardown >> dag_teardown
        # let's verify...
        cleared_tasks = partial(tasks_to_clear, dag)
        assert {x.task_id for x in g2_w2.get_upstreams_only_setups_and_teardowns()} == {
            "dag_setup",
            "dag_teardown",
            "g2.group_setup",
            "g2.group_teardown",
        }
        assert {x.task_id for x in cleared_tasks(g2_w2, upstream=True)} == {
            "dag_setup",
            "dag_teardown",
            "g2.group_setup",
            "g2.group_teardown",
            "g2.w1",
            "g2.w2",
        }
        assert {x.task_id for x in cleared_tasks(g2_w2, upstream=False)} == {
            "dag_setup",
            "dag_teardown",
            "g2.group_setup",
            "g2.group_teardown",
            "g2.w3",
            "g2.w2",
        }

    def test_get_flat_relative_ids_teardown_roots_ignored(self):
        dag = DAG(dag_id="test_dag", start_date=datetime.now())
        with dag:
            dag_setup = BaseOperator.as_setup(task_id="dag_setup")
            dag_teardown = BaseOperator.as_teardown(task_id="dag_teardown")
            w1 = BaseOperator(task_id="w1")
            w2 = BaseOperator(task_id="w2")
            w3 = BaseOperator(task_id="w3")
            dag_setup >> [w1, w2] >> w3
            w3 >> dag_teardown
            dag_setup >> dag_teardown
        assert dag_setup.get_direct_relative_ids(upstream=False) == {"w1", "w2", "dag_teardown"}
        assert dag_teardown.get_direct_relative_ids(upstream=True) == {"w3", "dag_setup"}
        # clearing a teardown should not clear the setups
        assert dag_teardown.get_direct_relative_ids(upstream=False) == set()

    def test_cross_downstream(self):
        """Test if all dependencies between tasks are all set correctly."""
        dag = DAG(dag_id="test_dag", start_date=datetime.now())
        start_tasks = [BaseOperator(task_id=f"t{i}", dag=dag) for i in range(1, 4)]
        end_tasks = [BaseOperator(task_id=f"t{i}", dag=dag) for i in range(4, 7)]
        cross_downstream(from_tasks=start_tasks, to_tasks=end_tasks)

        for start_task in start_tasks:
            assert set(start_task.get_direct_relatives(upstream=False)) == set(end_tasks)

        # Begin test for `XComArgs`
        xstart_tasks = [
            task_decorator(task_id=f"xcomarg_task{i}", python_callable=lambda: None, dag=dag)()
            for i in range(1, 4)
        ]
        xend_tasks = [
            task_decorator(task_id=f"xcomarg_task{i}", python_callable=lambda: None, dag=dag)()
            for i in range(4, 7)
        ]
        cross_downstream(from_tasks=xstart_tasks, to_tasks=xend_tasks)

        for xstart_task in xstart_tasks:
            assert set(xstart_task.operator.get_direct_relatives(upstream=False)) == {
                xend_task.operator for xend_task in xend_tasks
            }

    def test_chain(self):
        dag = DAG(dag_id="test_chain", start_date=datetime.now())

        # Begin test for classic operators with `EdgeModifiers`
        [label1, label2] = [Label(label=f"label{i}") for i in range(1, 3)]
        [op1, op2, op3, op4, op5, op6] = [BaseOperator(task_id=f"t{i}", dag=dag) for i in range(1, 7)]
        chain(op1, [label1, label2], [op2, op3], [op4, op5], op6)

        assert {op2, op3} == set(op1.get_direct_relatives(upstream=False))
        assert [op4] == op2.get_direct_relatives(upstream=False)
        assert [op5] == op3.get_direct_relatives(upstream=False)
        assert {op4, op5} == set(op6.get_direct_relatives(upstream=True))

        assert {"label": "label1"} == dag.get_edge_info(
            upstream_task_id=op1.task_id, downstream_task_id=op2.task_id
        )
        assert {"label": "label2"} == dag.get_edge_info(
            upstream_task_id=op1.task_id, downstream_task_id=op3.task_id
        )

        # Begin test for `XComArgs` with `EdgeModifiers`
        [xlabel1, xlabel2] = [Label(label=f"xcomarg_label{i}") for i in range(1, 3)]
        [xop1, xop2, xop3, xop4, xop5, xop6] = [
            task_decorator(task_id=f"xcomarg_task{i}", python_callable=lambda: None, dag=dag)()
            for i in range(1, 7)
        ]
        chain(xop1, [xlabel1, xlabel2], [xop2, xop3], [xop4, xop5], xop6)

        assert {xop2.operator, xop3.operator} == set(xop1.operator.get_direct_relatives(upstream=False))
        assert [xop4.operator] == xop2.operator.get_direct_relatives(upstream=False)
        assert [xop5.operator] == xop3.operator.get_direct_relatives(upstream=False)
        assert {xop4.operator, xop5.operator} == set(xop6.operator.get_direct_relatives(upstream=True))

        assert {"label": "xcomarg_label1"} == dag.get_edge_info(
            upstream_task_id=xop1.operator.task_id, downstream_task_id=xop2.operator.task_id
        )
        assert {"label": "xcomarg_label2"} == dag.get_edge_info(
            upstream_task_id=xop1.operator.task_id, downstream_task_id=xop3.operator.task_id
        )

        # Begin test for `TaskGroups`
        [tg1, tg2] = [TaskGroup(group_id=f"tg{i}", dag=dag) for i in range(1, 3)]
        [op1, op2] = [BaseOperator(task_id=f"task{i}", dag=dag) for i in range(1, 3)]
        [tgop1, tgop2] = [
            BaseOperator(task_id=f"task_group_task{i}", task_group=tg1, dag=dag) for i in range(1, 3)
        ]
        [tgop3, tgop4] = [
            BaseOperator(task_id=f"task_group_task{i}", task_group=tg2, dag=dag) for i in range(1, 3)
        ]
        chain(op1, tg1, tg2, op2)

        assert {tgop1, tgop2} == set(op1.get_direct_relatives(upstream=False))
        assert {tgop3, tgop4} == set(tgop1.get_direct_relatives(upstream=False))
        assert {tgop3, tgop4} == set(tgop2.get_direct_relatives(upstream=False))
        assert [op2] == tgop3.get_direct_relatives(upstream=False)
        assert [op2] == tgop4.get_direct_relatives(upstream=False)

    def test_chain_not_support_type(self):
        dag = DAG(dag_id="test_chain", start_date=datetime.now())
        [op1, op2] = [BaseOperator(task_id=f"t{i}", dag=dag) for i in range(1, 3)]
        with pytest.raises(TypeError):
            chain([op1, op2], 1)

        # Begin test for `XComArgs`
        [xop1, xop2] = [
            task_decorator(task_id=f"xcomarg_task{i}", python_callable=lambda: None, dag=dag)()
            for i in range(1, 3)
        ]

        with pytest.raises(TypeError):
            chain([xop1, xop2], 1)

        # Begin test for `EdgeModifiers`
        with pytest.raises(TypeError):
            chain([Label("labe1"), Label("label2")], 1)

        # Begin test for `TaskGroups`
        [tg1, tg2] = [TaskGroup(group_id=f"tg{i}", dag=dag) for i in range(1, 3)]

        with pytest.raises(TypeError):
            chain([tg1, tg2], 1)

    def test_chain_different_length_iterable(self):
        dag = DAG(dag_id="test_chain", start_date=datetime.now())
        [label1, label2] = [Label(label=f"label{i}") for i in range(1, 3)]
        [op1, op2, op3, op4, op5] = [BaseOperator(task_id=f"t{i}", dag=dag) for i in range(1, 6)]

        with pytest.raises(AirflowException):
            chain([op1, op2], [op3, op4, op5])

        with pytest.raises(AirflowException):
            chain([op1, op2, op3], [label1, label2])

        # Begin test for `XComArgs` with `EdgeModifiers`
        [label3, label4] = [Label(label=f"xcomarg_label{i}") for i in range(1, 3)]
        [xop1, xop2, xop3, xop4, xop5] = [
            task_decorator(task_id=f"xcomarg_task{i}", python_callable=lambda: None, dag=dag)()
            for i in range(1, 6)
        ]

        with pytest.raises(AirflowException):
            chain([xop1, xop2], [xop3, xop4, xop5])

        with pytest.raises(AirflowException):
            chain([xop1, xop2, xop3], [label1, label2])

        # Begin test for `TaskGroups`
        [tg1, tg2, tg3, tg4, tg5] = [TaskGroup(group_id=f"tg{i}", dag=dag) for i in range(1, 6)]

        with pytest.raises(AirflowException):
            chain([tg1, tg2], [tg3, tg4, tg5])

    def test_lineage_composition(self):
        """
        Test composition with lineage
        """
        inlet = File(url="in")
        outlet = File(url="out")
        dag = DAG("test-dag", start_date=DEFAULT_DATE)
        task1 = BaseOperator(task_id="op1", dag=dag)
        task2 = BaseOperator(task_id="op2", dag=dag)

        # mock
        task1.supports_lineage = True

        # note: operator precedence still applies
        inlet > task1 | (task2 > outlet)

        assert task1.get_inlet_defs() == [inlet]
        assert task2.get_inlet_defs() == [task1.task_id]
        assert task2.get_outlet_defs() == [outlet]

        fail = ClassWithCustomAttributes()
        with pytest.raises(TypeError):
            fail > task1
        with pytest.raises(TypeError):
            task1 > fail
        with pytest.raises(TypeError):
            fail | task1
        with pytest.raises(TypeError):
            task1 | fail

        task3 = BaseOperator(task_id="op3", dag=dag)
        extra = File(url="extra")
        [inlet, extra] > task3

        assert task3.get_inlet_defs() == [inlet, extra]

        task1.supports_lineage = False
        with pytest.raises(ValueError):
            task1 | task3

        assert task2.supports_lineage is False
        task2 | task3
        assert len(task3.get_inlet_defs()) == 3

        task4 = BaseOperator(task_id="op4", dag=dag)
        task4 > [inlet, outlet, extra]
        assert task4.get_outlet_defs() == [inlet, outlet, extra]

    def test_warnings_are_properly_propagated(self):
        with pytest.warns(DeprecationWarning) as warnings:
            DeprecatedOperator(task_id="test")
            assert len(warnings) == 1
            warning = warnings[0]
            # Here we check that the trace points to the place
            # where the deprecated class was used
            assert warning.filename == __file__

    def test_pre_execute_hook(self):
        hook = mock.MagicMock()

        op = BaseOperator(task_id="test_task", pre_execute=hook)
        op_copy = op.prepare_for_execution()
        op_copy.pre_execute({})
        assert hook.called

    def test_post_execute_hook(self):
        hook = mock.MagicMock()

        op = BaseOperator(task_id="test_task", post_execute=hook)
        op_copy = op.prepare_for_execution()
        op_copy.post_execute({})
        assert hook.called

    def test_task_naive_datetime(self):
        naive_datetime = DEFAULT_DATE.replace(tzinfo=None)

        op_no_dag = BaseOperator(
            task_id="test_task_naive_datetime", start_date=naive_datetime, end_date=naive_datetime
        )

        assert op_no_dag.start_date.tzinfo
        assert op_no_dag.end_date.tzinfo

    def test_setattr_performs_no_custom_action_at_execute_time(self):
        op = MockOperator(task_id="test_task")
        op_copy = op.prepare_for_execution()

        with mock.patch("airflow.models.baseoperator.BaseOperator.set_xcomargs_dependencies") as method_mock:
            op_copy.execute({})
        assert method_mock.call_count == 0

    def test_upstream_is_set_when_template_field_is_xcomarg(self):
        with DAG("xcomargs_test", default_args={"start_date": datetime.today()}):
            op1 = BaseOperator(task_id="op1")
            op2 = MockOperator(task_id="op2", arg1=op1.output)

        assert op1 in op2.upstream_list
        assert op2 in op1.downstream_list

    def test_set_xcomargs_dependencies_works_recursively(self):
        with DAG("xcomargs_test", default_args={"start_date": datetime.today()}):
            op1 = BaseOperator(task_id="op1")
            op2 = BaseOperator(task_id="op2")
            op3 = MockOperator(task_id="op3", arg1=[op1.output, op2.output])
            op4 = MockOperator(task_id="op4", arg1={"op1": op1.output, "op2": op2.output})

        assert op1 in op3.upstream_list
        assert op2 in op3.upstream_list
        assert op1 in op4.upstream_list
        assert op2 in op4.upstream_list

    def test_set_xcomargs_dependencies_works_when_set_after_init(self):
        with DAG(dag_id="xcomargs_test", default_args={"start_date": datetime.today()}):
            op1 = BaseOperator(task_id="op1")
            op2 = MockOperator(task_id="op2")
            op2.arg1 = op1.output  # value is set after init

        assert op1 in op2.upstream_list

    def test_set_xcomargs_dependencies_error_when_outside_dag(self):
        with pytest.raises(AirflowException):
            op1 = BaseOperator(task_id="op1")
            MockOperator(task_id="op2", arg1=op1.output)

    def test_invalid_trigger_rule(self):
        with pytest.raises(
            AirflowException,
            match=(
                f"The trigger_rule must be one of {TriggerRule.all_triggers()},"
                "'.op1'; received 'some_rule'."
            ),
        ):
            BaseOperator(task_id="op1", trigger_rule="some_rule")

    @pytest.mark.parametrize(("rule"), [("dummy"), (TriggerRule.DUMMY)])
    def test_replace_dummy_trigger_rule(self, rule):
        with pytest.warns(
            DeprecationWarning, match="dummy Trigger Rule is deprecated. Please use `TriggerRule.ALWAYS`."
        ):
            op1 = BaseOperator(task_id="op1", trigger_rule=rule)

            assert op1.trigger_rule == TriggerRule.ALWAYS

    def test_weight_rule_default(self):
        op = BaseOperator(task_id="test_task")
        assert WeightRule.DOWNSTREAM == op.weight_rule

    def test_weight_rule_override(self):
        op = BaseOperator(task_id="test_task", weight_rule="upstream")
        assert WeightRule.UPSTREAM == op.weight_rule

    # ensure the default logging config is used for this test, no matter what ran before
    @pytest.mark.usefixtures("reset_logging_config")
    def test_logging_propogated_by_default(self, caplog):
        """Test that when set_context hasn't been called that log records are emitted"""
        BaseOperator(task_id="test").log.warning("test")
        # This looks like "how could it fail" but this actually checks that the handler called `emit`. Testing
        # the other case (that when we have set_context it goes to the file is harder to achieve without
        # leaking a lot of state)
        assert caplog.messages == ["test"]


def test_init_subclass_args():
    class InitSubclassOp(BaseOperator):
        _class_arg: Any

        def __init_subclass__(cls, class_arg=None, **kwargs) -> None:
            cls._class_arg = class_arg
            super().__init_subclass__()

        def execute(self, context: Context):
            self.context_arg = context

    class_arg = "foo"
    context = {"key": "value"}

    class ConcreteSubclassOp(InitSubclassOp, class_arg=class_arg):
        pass

    task = ConcreteSubclassOp(task_id="op1")
    task_copy = task.prepare_for_execution()

    task_copy.execute(context)

    assert task_copy._class_arg == class_arg
    assert task_copy.context_arg == context


def test_operator_retries_invalid(dag_maker):
    with pytest.raises(AirflowException) as ctx:
        with dag_maker():
            BaseOperator(task_id="test_illegal_args", retries="foo")
    assert str(ctx.value) == "'retries' type must be int, not str"


@pytest.mark.parametrize(
    ("retries", "expected"),
    [
        pytest.param(None, [], id="None"),
        pytest.param(5, [], id="5"),
        pytest.param(
            "1",
            [
                (
                    "airflow.models.baseoperator.BaseOperator",
                    logging.WARNING,
                    "Implicitly converting 'retries' from '1' to int",
                ),
            ],
            id="str",
        ),
    ],
)
def test_operator_retries(caplog, dag_maker, retries, expected):
    with caplog.at_level(logging.WARNING):
        with dag_maker():
            BaseOperator(
                task_id="test_illegal_args",
                retries=retries,
            )
    assert caplog.record_tuples == expected


def test_default_retry_delay(dag_maker):
    with dag_maker(dag_id="test_default_retry_delay"):
        task1 = BaseOperator(task_id="test_no_explicit_retry_delay")

        assert task1.retry_delay == timedelta(seconds=300)


def test_dag_level_retry_delay(dag_maker):
    with dag_maker(dag_id="test_dag_level_retry_delay", default_args={"retry_delay": timedelta(seconds=100)}):
        task1 = BaseOperator(task_id="test_no_explicit_retry_delay")

        assert task1.retry_delay == timedelta(seconds=100)


def test_task_level_retry_delay(dag_maker):
    with dag_maker(
        dag_id="test_task_level_retry_delay", default_args={"retry_delay": timedelta(seconds=100)}
    ):
        task1 = BaseOperator(task_id="test_no_explicit_retry_delay", retry_delay=timedelta(seconds=200))

        assert task1.retry_delay == timedelta(seconds=200)


def test_deepcopy():
    # Test bug when copying an operator attached to a DAG
    with DAG("dag0", start_date=DEFAULT_DATE) as dag:

        @dag.task
        def task0():
            pass

        MockOperator(task_id="task1", arg1=task0())
    copy.deepcopy(dag)


@pytest.mark.parametrize(
    ("task", "context", "expected_exception", "expected_rendering", "expected_log", "not_expected_log"),
    [
        # Simple success case.
        (
            MockOperator(task_id="op1", arg1="{{ foo }}"),
            dict(foo="footemplated"),
            None,
            dict(arg1="footemplated"),
            None,
            "Exception rendering Jinja template",
        ),
        # Jinja syntax error.
        (
            MockOperator(task_id="op1", arg1="{{ foo"),
            dict(),
            jinja2.TemplateSyntaxError,
            None,
            "Exception rendering Jinja template for task 'op1', field 'arg1'. Template: '{{ foo'",
            None,
        ),
        # Type error
        (
            MockOperator(task_id="op1", arg1="{{ foo + 1 }}"),
            dict(foo="footemplated"),
            TypeError,
            None,
            "Exception rendering Jinja template for task 'op1', field 'arg1'. Template: '{{ foo + 1 }}'",
            None,
        ),
    ],
)
def test_render_template_fields_logging(
    caplog, monkeypatch, task, context, expected_exception, expected_rendering, expected_log, not_expected_log
):
    """Verify if operator attributes are correctly templated."""
    # Trigger templating and verify results
    def _do_render():
        task.render_template_fields(context=context)

    logger = logging.getLogger("airflow.task")
    monkeypatch.setattr(logger, "propagate", True)
    if expected_exception:
        with pytest.raises(expected_exception):
            _do_render()
    else:
        _do_render()
        for k, v in expected_rendering.items():
            assert getattr(task, k) == v
    if expected_log:
        assert expected_log in caplog.text
    if not_expected_log:
        assert not_expected_log not in caplog.text


def test_find_mapped_dependants_in_another_group(dag_maker):
    from airflow.utils.task_group import TaskGroup

    @task_decorator
    def gen(x):
        return list(range(x))

    @task_decorator
    def add(x, y):
        return x + y

    with dag_maker():
        with TaskGroup(group_id="g1"):
            gen_result = gen(3)
        with TaskGroup(group_id="g2"):
            add_result = add.partial(y=1).expand(x=gen_result)

    dependants = list(gen_result.operator.iter_mapped_dependants())
    assert dependants == [add_result.operator]
