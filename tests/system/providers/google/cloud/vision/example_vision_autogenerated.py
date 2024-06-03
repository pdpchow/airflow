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

import os
from datetime import datetime

from airflow.models.baseoperator import chain
from airflow.models.dag import DAG
from airflow.providers.google.cloud.operators.gcs import GCSCreateBucketOperator, GCSDeleteBucketOperator
from airflow.providers.google.cloud.operators.vision import (
    CloudVisionAddProductToProductSetOperator,
    CloudVisionCreateProductOperator,
    CloudVisionCreateProductSetOperator,
    CloudVisionCreateReferenceImageOperator,
    CloudVisionDeleteProductOperator,
    CloudVisionDeleteProductSetOperator,
    CloudVisionDeleteReferenceImageOperator,
    CloudVisionGetProductOperator,
    CloudVisionGetProductSetOperator,
    CloudVisionRemoveProductFromProductSetOperator,
    CloudVisionUpdateProductOperator,
    CloudVisionUpdateProductSetOperator,
)
from airflow.providers.google.cloud.transfers.gcs_to_gcs import GCSToGCSOperator
from airflow.utils.trigger_rule import TriggerRule

# [START howto_operator_vision_retry_import]
from google.api_core.retry import Retry  # isort:skip

# [END howto_operator_vision_retry_import]
# [START howto_operator_vision_product_set_import]
from google.cloud.vision_v1.types import ProductSet  # isort:skip

# [END howto_operator_vision_product_set_import]
# [START howto_operator_vision_product_import]
from google.cloud.vision_v1.types import Product  # isort:skip

# [END howto_operator_vision_product_import]
# [START howto_operator_vision_reference_image_import]
from google.cloud.vision_v1.types import ReferenceImage  # isort:skip

# [END howto_operator_vision_reference_image_import]
# [START howto_operator_vision_enums_import]
from google.cloud.vision_v1 import Feature  # isort:skip
from tests.system.providers.google import DEFAULT_GCP_SYSTEM_TEST_PROJECT_ID

# [END howto_operator_vision_enums_import]

ENV_ID = os.environ.get("SYSTEM_TESTS_ENV_ID")
PROJECT_ID = os.environ.get("SYSTEM_TESTS_GCP_PROJECT") or DEFAULT_GCP_SYSTEM_TEST_PROJECT_ID

DAG_ID = "example_gcp_vision_autogenerated_id"

LOCATION = "europe-west1"

BUCKET_NAME = f"bucket-{DAG_ID}-{ENV_ID}"
FILE_NAME = "image1.jpg"

GCP_VISION_PRODUCT_SET_ID = "product_set_explicit_id"
GCP_VISION_PRODUCT_ID = "product_explicit_id"
GCP_VISION_REFERENCE_IMAGE_ID = f"reference_image_explicit_id-{ENV_ID}"

VISION_IMAGE_URL = f"gs://{BUCKET_NAME}/{FILE_NAME}"

# [START howto_operator_vision_product_set]
product_set = ProductSet(display_name="My Product Set")
# [END howto_operator_vision_product_set]

# [START howto_operator_vision_product]
product = Product(display_name="My Product 1", product_category="toys")
# [END howto_operator_vision_product]

# [START howto_operator_vision_reference_image]
reference_image = ReferenceImage(uri=VISION_IMAGE_URL)
# [END howto_operator_vision_reference_image]

# [START howto_operator_vision_annotate_image_request]
annotate_image_request = {
    "image": {"source": {"image_uri": VISION_IMAGE_URL}},
    "features": [{"type_": Feature.Type.LOGO_DETECTION}],
}
# [END howto_operator_vision_annotate_image_request]

# [START howto_operator_vision_detect_image_param]
DETECT_IMAGE = {"source": {"image_uri": VISION_IMAGE_URL}}
# [END howto_operator_vision_detect_image_param]

# Public bucket holding the sample data
BUCKET_NAME_SRC = "cloud-samples-data"
# Path to the data inside the public bucket
PATH_SRC = "vision/ocr/sign.jpg"

with DAG(
    DAG_ID,
    schedule="@once",
    start_date=datetime(2021, 1, 1),
    catchup=False,
    tags=["example", "vision"],
) as dag:
    create_bucket = GCSCreateBucketOperator(
        task_id="create_bucket", project_id=PROJECT_ID, bucket_name=BUCKET_NAME
    )

    copy_single_file = GCSToGCSOperator(
        task_id="copy_single_gcs_file",
        source_bucket=BUCKET_NAME_SRC,
        source_object=[PATH_SRC],
        destination_bucket=BUCKET_NAME,
        destination_object=FILE_NAME,
    )

    # [START howto_operator_vision_product_set_create]
    product_set_create = CloudVisionCreateProductSetOperator(
        location=LOCATION,
        product_set=product_set,
        retry=Retry(maximum=10.0),
        timeout=5,
        task_id="product_set_create",
    )
    # [END howto_operator_vision_product_set_create]

    product_set_create_output = "{{ task_instance.xcom_pull('product_set_create') }}"

    # [START howto_operator_vision_product_set_get]
    product_set_get = CloudVisionGetProductSetOperator(
        location=LOCATION,
        product_set_id=product_set_create_output,
        task_id="product_set_get",
    )
    # [END howto_operator_vision_product_set_get]

    # [START howto_operator_vision_product_set_update]
    product_set_update = CloudVisionUpdateProductSetOperator(
        location=LOCATION,
        product_set_id=product_set_create_output,
        product_set=ProductSet(display_name="My Product Set 2"),
        task_id="product_set_update",
    )
    # [END howto_operator_vision_product_set_update]

    # [START howto_operator_vision_product_set_delete]
    product_set_delete = CloudVisionDeleteProductSetOperator(
        location=LOCATION,
        product_set_id=product_set_create_output,
        task_id="product_set_delete",
    )
    # [END howto_operator_vision_product_set_delete]

    # [START howto_operator_vision_product_create]
    product_create = CloudVisionCreateProductOperator(
        location=LOCATION,
        product=product,
        retry=Retry(maximum=10.0),
        timeout=5,
        task_id="product_create",
    )
    # [END howto_operator_vision_product_create]

    # [START howto_operator_vision_product_get]
    product_get = CloudVisionGetProductOperator(
        location=LOCATION,
        product_id="{{ task_instance.xcom_pull('product_create') }}",
        task_id="product_get",
    )
    # [END howto_operator_vision_product_get]

    # [START howto_operator_vision_product_update]
    product_update = CloudVisionUpdateProductOperator(
        location=LOCATION,
        product_id="{{ task_instance.xcom_pull('product_create') }}",
        product=Product(display_name="My Product 2", description="My updated description"),
        task_id="product_update",
    )
    # [END howto_operator_vision_product_update]

    # [START howto_operator_vision_product_delete]
    product_delete = CloudVisionDeleteProductOperator(
        location=LOCATION,
        product_id="{{ task_instance.xcom_pull('product_create') }}",
        task_id="product_delete",
    )
    # [END howto_operator_vision_product_delete]

    # [START howto_operator_vision_reference_image_create]
    reference_image_create = CloudVisionCreateReferenceImageOperator(
        location=LOCATION,
        reference_image=reference_image,
        product_id="{{ task_instance.xcom_pull('product_create') }}",
        reference_image_id=GCP_VISION_REFERENCE_IMAGE_ID,
        retry=Retry(maximum=10.0),
        timeout=5,
        task_id="reference_image_create",
    )
    # [END howto_operator_vision_reference_image_create]

    # [START howto_operator_vision_reference_image_delete]
    reference_image_delete = CloudVisionDeleteReferenceImageOperator(
        location=LOCATION,
        product_id="{{ task_instance.xcom_pull('product_create') }}",
        reference_image_id=GCP_VISION_REFERENCE_IMAGE_ID,
        retry=Retry(maximum=10.0),
        timeout=5,
        task_id="reference_image_delete",
    )
    # [END howto_operator_vision_reference_image_delete]

    # [START howto_operator_vision_add_product_to_product_set]
    add_product_to_product_set = CloudVisionAddProductToProductSetOperator(
        location=LOCATION,
        product_set_id=product_set_create_output,
        product_id="{{ task_instance.xcom_pull('product_create') }}",
        retry=Retry(maximum=10.0),
        timeout=5,
        task_id="add_product_to_product_set",
    )
    # [END howto_operator_vision_add_product_to_product_set]

    # [START howto_operator_vision_remove_product_from_product_set]
    remove_product_from_product_set = CloudVisionRemoveProductFromProductSetOperator(
        location=LOCATION,
        product_set_id=product_set_create_output,
        product_id="{{ task_instance.xcom_pull('product_create') }}",
        retry=Retry(maximum=10.0),
        timeout=5,
        task_id="remove_product_from_product_set",
    )
    # [END howto_operator_vision_remove_product_from_product_set]

    delete_bucket = GCSDeleteBucketOperator(
        task_id="delete_bucket", bucket_name=BUCKET_NAME, trigger_rule=TriggerRule.ALL_DONE
    )

    chain(
        create_bucket,
        copy_single_file,
        product_create,
        product_get,
        product_update,
        product_set_create,
        product_set_get,
        product_set_update,
        reference_image_create,
        add_product_to_product_set,
        reference_image_delete,
        remove_product_from_product_set,
        product_set_delete,
        product_delete,
        delete_bucket,
    )

    from tests.system.utils.watcher import watcher

    # This test needs watcher in order to properly mark success/failure
    # when "teardown" task with trigger rule is part of the DAG
    list(dag.tasks) >> watcher()


from tests.system.utils import get_test_run  # noqa: E402

# Needed to run the example DAG with pytest (see: tests/system/README.md#run_via_pytest)
test_run = get_test_run(dag)
