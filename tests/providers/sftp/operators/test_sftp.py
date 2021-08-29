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

import os
import shutil
import unittest
from base64 import b64encode
from unittest import mock

import pytest

from airflow.exceptions import AirflowException
from airflow.models import DAG, TaskInstance
from airflow.providers.sftp.operators.sftp import SFTPOperation, SFTPOperator
from airflow.providers.ssh.operators.ssh import SSHOperator
from airflow.utils import timezone
from airflow.utils.timezone import datetime
from tests.test_utils.config import conf_vars

TEST_DAG_ID = 'unit_tests_sftp_op'
DEFAULT_DATE = datetime(2017, 1, 1)
TEST_CONN_ID = "conn_id_for_testing"


class TestSFTPOperator(unittest.TestCase):
    def setUp(self):
        from airflow.providers.ssh.hooks.ssh import SSHHook

        hook = SSHHook(ssh_conn_id='ssh_default')
        hook.no_host_key_check = True
        args = {
            'owner': 'airflow',
            'start_date': DEFAULT_DATE,
        }
        dag = DAG(TEST_DAG_ID + 'test_schedule_dag_once', default_args=args)
        dag.schedule_interval = '@once'
        self.hook = hook
        self.dag = dag
        self.test_dir = "/tmp"
        self.test_local_dir = "/tmp/tmp2"
        self.test_remote_dir = "/tmp/tmp1"
        self.test_local_filename = 'test_local_file'
        self.test_remote_filename = 'test_remote_file'
        self.test_local_filepath = f'{self.test_dir}/{self.test_local_filename}'
        # Local Filepath with Intermediate Directory
        self.test_local_filepath_int_dir = f'{self.test_local_dir}/{self.test_local_filename}'
        self.test_remote_filepath = f'{self.test_dir}/{self.test_remote_filename}'
        # Remote Filepath with Intermediate Directory
        self.test_remote_filepath_int_dir = f'{self.test_remote_dir}/{self.test_remote_filename}'
        self.test_txt_file = 'file1.txt'
        self.test_csv_file = 'file1.csv'

    @conf_vars({('core', 'enable_xcom_pickling'): 'True'})
    def test_pickle_file_transfer_put(self):
        test_local_file_content = (
            b"This is local file content \n which is multiline "
            b"continuing....with other character\nanother line here \n this is last line"
        )
        # create a test file locally
        with open(self.test_local_filepath, 'wb') as file:
            file.write(test_local_file_content)

        # put test file to remote
        put_test_task = SFTPOperator(
            task_id="put_test_task",
            ssh_hook=self.hook,
            local_filepath=self.test_local_filepath,
            remote_filepath=self.test_remote_filepath,
            operation=SFTPOperation.PUT,
            create_intermediate_dirs=True,
            dag=self.dag,
        )
        assert put_test_task is not None
        ti2 = TaskInstance(task=put_test_task, execution_date=timezone.utcnow())
        ti2.run()

        # check the remote file content
        check_file_task = SSHOperator(
            task_id="check_file_task",
            ssh_hook=self.hook,
            command=f"cat {self.test_remote_filepath}",
            do_xcom_push=True,
            dag=self.dag,
        )
        assert check_file_task is not None
        ti3 = TaskInstance(task=check_file_task, execution_date=timezone.utcnow())
        ti3.run()
        assert (
            ti3.xcom_pull(task_ids=check_file_task.task_id, key='return_value').strip()
            == test_local_file_content
        )

    @conf_vars({('core', 'enable_xcom_pickling'): 'True'})
    def test_file_transfer_no_intermediate_dir_error_put(self):
        test_local_file_content = (
            b"This is local file content \n which is multiline "
            b"continuing....with other character\nanother line here \n this is last line"
        )
        # create a test file locally
        with open(self.test_local_filepath, 'wb') as file:
            file.write(test_local_file_content)

        # Try to put test file to remote
        # This should raise an error with "No such file" as the directory
        # does not exist
        with pytest.raises(Exception) as ctx:
            put_test_task = SFTPOperator(
                task_id="test_sftp",
                ssh_hook=self.hook,
                local_filepath=self.test_local_filepath,
                remote_filepath=self.test_remote_filepath_int_dir,
                operation=SFTPOperation.PUT,
                create_intermediate_dirs=False,
                dag=self.dag,
            )
            assert put_test_task is not None
            ti2 = TaskInstance(task=put_test_task, execution_date=timezone.utcnow())
            ti2.run()
        assert 'No such file' in str(ctx.value)

    @conf_vars({('core', 'enable_xcom_pickling'): 'True'})
    def test_file_transfer_with_intermediate_dir_put(self):
        test_local_file_content = (
            b"This is local file content \n which is multiline "
            b"continuing....with other character\nanother line here \n this is last line"
        )
        # create a test file locally
        with open(self.test_local_filepath, 'wb') as file:
            file.write(test_local_file_content)

        # put test file to remote
        put_test_task = SFTPOperator(
            task_id="test_sftp",
            ssh_hook=self.hook,
            local_filepath=self.test_local_filepath,
            remote_filepath=self.test_remote_filepath_int_dir,
            operation=SFTPOperation.PUT,
            create_intermediate_dirs=True,
            dag=self.dag,
        )
        assert put_test_task is not None
        ti2 = TaskInstance(task=put_test_task, execution_date=timezone.utcnow())
        ti2.run()

        # check the remote file content
        check_file_task = SSHOperator(
            task_id="test_check_file",
            ssh_hook=self.hook,
            command=f"cat {self.test_remote_filepath_int_dir}",
            do_xcom_push=True,
            dag=self.dag,
        )
        assert check_file_task is not None
        ti3 = TaskInstance(task=check_file_task, execution_date=timezone.utcnow())
        ti3.run()
        assert (
            ti3.xcom_pull(task_ids='test_check_file', key='return_value').strip() == test_local_file_content
        )

    @conf_vars({('core', 'enable_xcom_pickling'): 'False'})
    def test_json_file_transfer_put(self):
        test_local_file_content = (
            b"This is local file content \n which is multiline "
            b"continuing....with other character\nanother line here \n this is last line"
        )
        # create a test file locally
        with open(self.test_local_filepath, 'wb') as file:
            file.write(test_local_file_content)

        # put test file to remote
        put_test_task = SFTPOperator(
            task_id="put_test_task",
            ssh_hook=self.hook,
            local_filepath=self.test_local_filepath,
            remote_filepath=self.test_remote_filepath,
            operation=SFTPOperation.PUT,
            dag=self.dag,
        )
        assert put_test_task is not None
        ti2 = TaskInstance(task=put_test_task, execution_date=timezone.utcnow())
        ti2.run()

        # check the remote file content
        check_file_task = SSHOperator(
            task_id="check_file_task",
            ssh_hook=self.hook,
            command=f"cat {self.test_remote_filepath}",
            do_xcom_push=True,
            dag=self.dag,
        )
        assert check_file_task is not None
        ti3 = TaskInstance(task=check_file_task, execution_date=timezone.utcnow())
        ti3.run()
        assert ti3.xcom_pull(task_ids=check_file_task.task_id, key='return_value').strip() == b64encode(
            test_local_file_content
        ).decode('utf-8')

    @conf_vars({('core', 'enable_xcom_pickling'): 'True'})
    def test_pickle_file_transfer_get(self):
        test_remote_file_content = (
            "This is remote file content \n which is also multiline "
            "another line here \n this is last line. EOF"
        )

        # create a test file remotely
        create_file_task = SSHOperator(
            task_id="test_create_file",
            ssh_hook=self.hook,
            command=f"echo '{test_remote_file_content}' > {self.test_remote_filepath}",
            do_xcom_push=True,
            dag=self.dag,
        )
        assert create_file_task is not None
        ti1 = TaskInstance(task=create_file_task, execution_date=timezone.utcnow())
        ti1.run()

        # get remote file to local
        get_test_task = SFTPOperator(
            task_id="test_sftp",
            ssh_hook=self.hook,
            local_filepath=self.test_local_filepath,
            remote_filepath=self.test_remote_filepath,
            operation=SFTPOperation.GET,
            dag=self.dag,
        )
        assert get_test_task is not None
        ti2 = TaskInstance(task=get_test_task, execution_date=timezone.utcnow())
        ti2.run()

        # test the received content
        content_received = None
        with open(self.test_local_filepath) as file:
            content_received = file.read()
        assert content_received.strip() == test_remote_file_content

    @conf_vars({('core', 'enable_xcom_pickling'): 'False'})
    def test_json_file_transfer_get(self):
        test_remote_file_content = (
            "This is remote file content \n which is also multiline "
            "another line here \n this is last line. EOF"
        )

        # create a test file remotely
        create_file_task = SSHOperator(
            task_id="test_create_file",
            ssh_hook=self.hook,
            command=f"echo '{test_remote_file_content}' > {self.test_remote_filepath}",
            do_xcom_push=True,
            dag=self.dag,
        )
        assert create_file_task is not None
        ti1 = TaskInstance(task=create_file_task, execution_date=timezone.utcnow())
        ti1.run()

        # get remote file to local
        get_test_task = SFTPOperator(
            task_id="test_sftp",
            ssh_hook=self.hook,
            local_filepath=self.test_local_filepath,
            remote_filepath=self.test_remote_filepath,
            operation=SFTPOperation.GET,
            dag=self.dag,
        )
        assert get_test_task is not None
        ti2 = TaskInstance(task=get_test_task, execution_date=timezone.utcnow())
        ti2.run()

        # test the received content
        content_received = None
        with open(self.test_local_filepath) as file:
            content_received = file.read()
        assert content_received.strip() == test_remote_file_content.encode('utf-8').decode('utf-8')

    @conf_vars({('core', 'enable_xcom_pickling'): 'True'})
    def test_file_transfer_no_intermediate_dir_error_get(self):
        test_remote_file_content = (
            "This is remote file content \n which is also multiline "
            "another line here \n this is last line. EOF"
        )

        # create a test file remotely
        create_file_task = SSHOperator(
            task_id="test_create_file",
            ssh_hook=self.hook,
            command=f"echo '{test_remote_file_content}' > {self.test_remote_filepath}",
            do_xcom_push=True,
            dag=self.dag,
        )
        assert create_file_task is not None
        ti1 = TaskInstance(task=create_file_task, execution_date=timezone.utcnow())
        ti1.run()

        # Try to GET test file from remote
        # This should raise an error with "No such file" as the directory
        # does not exist
        with pytest.raises(Exception) as ctx:
            get_test_task = SFTPOperator(
                task_id="test_sftp",
                ssh_hook=self.hook,
                local_filepath=self.test_local_filepath_int_dir,
                remote_filepath=self.test_remote_filepath,
                operation=SFTPOperation.GET,
                dag=self.dag,
            )
            assert get_test_task is not None
            ti2 = TaskInstance(task=get_test_task, execution_date=timezone.utcnow())
            ti2.run()
        assert 'No such file' in str(ctx.value)

    @conf_vars({('core', 'enable_xcom_pickling'): 'True'})
    def test_transfer_many_files(self):
        test_output = f"{self.test_csv_file}\n{self.test_txt_file}"
        test_local_file_content = (
            b"This is remote file content \n which is also multiline "
            b"another line here \n this is last line. EOF"
        )
        os.mkdir(self.test_local_dir)
        with open(f'{self.test_local_dir}/{self.test_txt_file}', 'wb') as f:
            f.write(test_local_file_content)
        with open(f'{self.test_local_dir}/{self.test_csv_file}', 'wb') as f:
            f.write(test_local_file_content)
        put_files = SFTPOperator(
            task_id="put_files",
            ssh_hook=self.hook,
            local_filepath=[
                f"{self.test_local_dir}/{self.test_txt_file}",
                f"{self.test_local_dir}/{self.test_csv_file}",
            ],
            remote_filepath=self.test_remote_dir,
            operation=SFTPOperation.PUT,
            create_intermediate_dirs=True,
            dag=self.dag,
        )
        assert put_files is not None
        ti1 = TaskInstance(task=put_files, execution_date=timezone.utcnow())
        ti1.run()

        show_files = SSHOperator(
            task_id="show_files",
            ssh_hook=self.hook,
            command=f"ls {self.test_remote_dir}",
            do_xcom_push=True,
            dag=self.dag,
        )
        ti2 = TaskInstance(task=show_files, execution_date=timezone.utcnow())
        ti2.run()
        assert ti2.xcom_pull(task_ids=show_files.task_id, key='return_value').strip() == test_output.encode('utf8')

    @conf_vars({('core', 'enable_xcom_pickling'): 'True'})
    def test_transfer_regexp_files(self):
        test_txt_file_content = b"is txt file"
        test_csv_file_content = b"is csv file"
        os.mkdir(self.test_local_dir)
        with open(f'{self.test_local_dir}/{self.test_txt_file}', 'wb') as f:
            f.write(test_txt_file_content)
        with open(f'{self.test_local_dir}/{self.test_csv_file}', 'wb') as f:
            f.write(test_csv_file_content)
        put_files = SFTPOperator(
            task_id="put_files",
            ssh_hook=self.hook,
            local_folder=self.test_local_dir,
            remote_folder=self.test_remote_dir,
            regexp_mask=".*.txt",
            operation=SFTPOperation.PUT,
            create_intermediate_dirs=True,
            dag=self.dag,
        )
        assert put_files is not None
        ti1 = TaskInstance(task=put_files, execution_date=timezone.utcnow())
        ti1.run()

        show_files = SSHOperator(
            task_id="show_files",
            ssh_hook=self.hook,
            command=fr"find {self.test_remote_dir} -maxdepth 1 -type f -not -path '*/\.*' | wc -l",
            do_xcom_push=True,
            dag=self.dag,
        )
        ti2 = TaskInstance(task=show_files, execution_date=timezone.utcnow())
        ti2.run()
        assert ti2.xcom_pull(task_ids=show_files.task_id, key='return_value').strip() == b"1"

    @conf_vars({('core', 'enable_xcom_pickling'): 'True'})
    def test_transfer_many_files_to_local(self):
        test_txt_file_content = "is txt file"
        test_csv_file_content = "is csv file"
        create_file_task = SSHOperator(
            task_id="test_create_file",
            ssh_hook=self.hook,
            command=f"mkdir -p {self.test_remote_dir} && "
            f"echo '{test_txt_file_content}' >> {self.test_remote_dir}/{self.test_txt_file} && "
            f"echo '{test_csv_file_content}' >> {self.test_remote_dir}/{self.test_csv_file}",
            do_xcom_push=False,
            dag=self.dag,
        )
        assert create_file_task is not None
        ti0 = TaskInstance(task=create_file_task, execution_date=timezone.utcnow())
        ti0.run()

        get_files = SFTPOperator(
            task_id="get_files",
            ssh_hook=self.hook,
            local_filepath=self.test_local_dir,
            remote_filepath=[f"{self.test_remote_dir}/{self.test_txt_file}",
                             f"{self.test_remote_dir}/{self.test_csv_file}"],
            operation=SFTPOperation.GET,
            create_intermediate_dirs=True,
            dag=self.dag,
        )
        assert get_files is not None
        ti1 = TaskInstance(task=get_files, execution_date=timezone.utcnow())
        ti1.run()

        show_files = SSHOperator(
            task_id="show_files",
            ssh_hook=self.hook,
            command=fr"find {self.test_local_dir} -maxdepth 1 -type f -not -path '*/\.*' | wc -l",
            do_xcom_push=True,
            dag=self.dag,
        )
        ti2 = TaskInstance(task=show_files, execution_date=timezone.utcnow())
        ti2.run()
        assert ti2.xcom_pull(task_ids=show_files.task_id, key='return_value').strip() == b"2"

    @conf_vars({('core', 'enable_xcom_pickling'): 'True'})
    def test_transfer_all_files_to_local(self):
        test_txt_file_content = "is txt file"
        test_csv_file_content = "is csv file"

        create_file_task = SSHOperator(
            task_id="test_create_file",
            ssh_hook=self.hook,
            command=f"mkdir -p {self.test_remote_dir} && "
            f"echo '{test_txt_file_content}' >> {self.test_remote_dir}/{self.test_txt_file} && "
            f"echo '{test_csv_file_content}' >> {self.test_remote_dir}/{self.test_csv_file}",
            do_xcom_push=False,
            dag=self.dag,
        )
        assert create_file_task is not None
        ti0 = TaskInstance(task=create_file_task, execution_date=timezone.utcnow())
        ti0.run()

        get_files = SFTPOperator(
            task_id="get_files",
            ssh_hook=self.hook,
            local_folder=self.test_local_dir,
            remote_folder=self.test_remote_dir,
            operation=SFTPOperation.GET,
            create_intermediate_dirs=True,
            dag=self.dag,
        )
        assert get_files is not None
        ti1 = TaskInstance(task=get_files, execution_date=timezone.utcnow())
        ti1.run()

        show_files = SSHOperator(
            task_id="show_files",
            ssh_hook=self.hook,
            command=fr"find {self.test_local_dir} -maxdepth 1 -type f -not -path '*/\.*' | wc -l",
            do_xcom_push=True,
            dag=self.dag,
        )
        ti2 = TaskInstance(task=show_files, execution_date=timezone.utcnow())
        ti2.run()
        assert ti2.xcom_pull(task_ids=show_files.task_id, key='return_value').strip() == b"2"

    @conf_vars({('core', 'enable_xcom_pickling'): 'True'})
    def test_transfer_all_files_to_remote(self):
        test_txt_file_content = b"is txt file"
        test_csv_file_content = b"is csv file"
        os.mkdir(self.test_local_dir)
        with open(f'{self.test_local_dir}/{self.test_txt_file}', 'wb') as f:
            f.write(test_txt_file_content)
        with open(f'{self.test_local_dir}/{self.test_csv_file}', 'wb') as f:
            f.write(test_csv_file_content)
        get_files = SFTPOperator(
            task_id="get_files",
            ssh_hook=self.hook,
            local_folder=self.test_local_dir,
            remote_folder=self.test_remote_dir,
            operation=SFTPOperation.PUT,
            create_intermediate_dirs=True,
            dag=self.dag,
        )
        assert get_files is not None
        ti1 = TaskInstance(task=get_files, execution_date=timezone.utcnow())
        ti1.run()

        show_files = SSHOperator(
            task_id="show_files",
            ssh_hook=self.hook,
            command=f"find {self.test_remote_dir} -maxdepth 1 -type f -not -path '*/\.*' | wc -l",
            do_xcom_push=True,
            dag=self.dag,
        )
        ti2 = TaskInstance(task=show_files, execution_date=timezone.utcnow())
        ti2.run()
        assert (
            ti2.xcom_pull(task_ids=show_files.task_id, key='return_value').strip()
            == b"2"
        )

    @conf_vars({('core', 'enable_xcom_pickling'): 'True'})
    def test_file_transfer_with_intermediate_dir_error_get(self):
        test_remote_file_content = (
            "This is remote file content \n which is also multiline "
            "another line here \n this is last line. EOF"
        )

        # create a test file remotely
        create_file_task = SSHOperator(
            task_id="test_create_file",
            ssh_hook=self.hook,
            command=f"echo '{test_remote_file_content}' > {self.test_remote_filepath}",
            do_xcom_push=True,
            dag=self.dag,
        )
        assert create_file_task is not None
        ti1 = TaskInstance(task=create_file_task, execution_date=timezone.utcnow())
        ti1.run()

        # get remote file to local
        get_test_task = SFTPOperator(
            task_id="test_sftp",
            ssh_hook=self.hook,
            local_filepath=self.test_local_filepath_int_dir,
            remote_filepath=self.test_remote_filepath,
            operation=SFTPOperation.GET,
            create_intermediate_dirs=True,
            dag=self.dag,
        )
        assert get_test_task is not None
        ti2 = TaskInstance(task=get_test_task, execution_date=timezone.utcnow())
        ti2.run()

        # test the received content
        content_received = None
        with open(self.test_local_filepath_int_dir) as file:
            content_received = file.read()
        assert content_received.strip() == test_remote_file_content

    @mock.patch.dict('os.environ', {'AIRFLOW_CONN_' + TEST_CONN_ID.upper(): "ssh://test_id@localhost"})
    def test_arg_checking(self):
        # Exception should be raised if neither ssh_hook nor ssh_conn_id is provided
        with pytest.raises(AirflowException, match="Cannot operate without ssh_hook or ssh_conn_id."):
            task_0 = SFTPOperator(
                task_id="test_sftp_0",
                local_filepath=self.test_local_filepath,
                remote_filepath=self.test_remote_filepath,
                operation=SFTPOperation.PUT,
                dag=self.dag,
            )
            task_0.execute(None)

        # if ssh_hook is invalid/not provided, use ssh_conn_id to create SSHHook
        task_1 = SFTPOperator(
            task_id="test_sftp_1",
            ssh_hook="string_rather_than_SSHHook",  # invalid ssh_hook
            ssh_conn_id=TEST_CONN_ID,
            local_filepath=self.test_local_filepath,
            remote_filepath=self.test_remote_filepath,
            operation=SFTPOperation.PUT,
            dag=self.dag,
        )
        try:
            task_1.execute(None)
        except Exception:
            pass
        assert task_1.ssh_hook.ssh_conn_id == TEST_CONN_ID

        task_2 = SFTPOperator(
            task_id="test_sftp_2",
            ssh_conn_id=TEST_CONN_ID,  # no ssh_hook provided
            local_filepath=self.test_local_filepath,
            remote_filepath=self.test_remote_filepath,
            operation=SFTPOperation.PUT,
            dag=self.dag,
        )
        try:
            task_2.execute(None)
        except Exception:
            pass
        assert task_2.ssh_hook.ssh_conn_id == TEST_CONN_ID

        # if both valid ssh_hook and ssh_conn_id are provided, ignore ssh_conn_id
        task_3 = SFTPOperator(
            task_id="test_sftp_3",
            ssh_hook=self.hook,
            ssh_conn_id=TEST_CONN_ID,
            local_filepath=self.test_local_filepath,
            remote_filepath=self.test_remote_filepath,
            operation=SFTPOperation.PUT,
            dag=self.dag,
        )
        try:
            task_3.execute(None)
        except Exception:
            pass
        assert task_3.ssh_hook.ssh_conn_id == self.hook.ssh_conn_id

        # when you work with specific files, then you should use *_files arguments
        task_4 = SFTPOperator(
            task_id="task_4",
            ssh_conn_id=TEST_CONN_ID,
            local_folder="/tmp/dir_for_remote_transfer/from_remote/csv/",
            remote_filepath=[
                "/tmp/transfer_file/remote/put_files_file1.txt",
                "/tmp/transfer_file/remote/put_files_file2.txt",
            ],
            operation=SFTPOperation.GET,
            create_intermediate_dirs=True,
        )
        try:
            task_4.execute(None)
        except Exception:
            pass
        assert task_4.local_filepath is None

    def delete_local_resource(self):
        if os.path.exists(self.test_local_filepath):
            if os.path.isdir(self.test_local_filepath):
                shutil.rmtree(self.test_local_filepath)
            else:
                os.remove(self.test_local_filepath)
        if os.path.exists(self.test_local_filepath_int_dir):
            if os.path.isdir(self.test_local_filepath_int_dir):
                shutil.rmtree(self.test_local_filepath_int_dir)
            else:
                os.remove(self.test_local_filepath_int_dir)
        if os.path.exists(self.test_local_dir):
            if os.path.isdir(self.test_local_dir):
                shutil.rmtree(self.test_local_dir)
            else:
                os.remove(self.test_local_dir)

    def delete_remote_resource(self):
        if os.path.exists(self.test_remote_filepath):
            # check the remote file content
            remove_file_task = SSHOperator(
                task_id="test_check_file",
                ssh_hook=self.hook,
                command=f"rm -rf {self.test_remote_filepath}",
                do_xcom_push=True,
                dag=self.dag,
            )
            assert remove_file_task is not None
            ti3 = TaskInstance(task=remove_file_task, execution_date=timezone.utcnow())
            ti3.run()
        if os.path.exists(self.test_remote_filepath_int_dir):
            os.remove(self.test_remote_filepath_int_dir)
        if os.path.exists(self.test_remote_dir):
            import shutil
            shutil.rmtree(self.test_remote_dir)

    def tearDown(self):
        self.delete_local_resource()
        self.delete_remote_resource()
