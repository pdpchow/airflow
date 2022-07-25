/*!
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */
import React, { useMemo } from 'react';
import {
  Box, Heading, Text,
} from '@chakra-ui/react';

import {
  CodeCell, DatasetLink, GridLink, RunLink, Table, TaskInstanceLink, TimeCell,
} from 'src/components/Table';
import { useUpstreamDatasetEvents } from 'src/api';
import type { DagRun as DagRunType } from 'src/types';

interface Props {
  runId: DagRunType['runId'];
}

const UpstreamEvents = ({ runId }: Props) => {
  const { data: { datasetEvents }, isLoading } = useUpstreamDatasetEvents({ runId });

  const columns = useMemo(
    () => [
      {
        Header: 'Dataset ID',
        accessor: 'datasetId',
        Cell: DatasetLink,
      },
      {
        Header: 'Created At',
        accessor: 'createdAt',
        Cell: TimeCell,
      },
      {
        Header: 'Source DAG',
        accessor: 'sourceDagId',
        Cell: GridLink,
      },
      {
        Header: 'Source DAG Run',
        accessor: 'sourceRunId',
        Cell: RunLink,
      },
      {
        Header: 'Source Task',
        accessor: 'sourceTaskId',
        Cell: TaskInstanceLink,
      },
      {
        Header: 'Source Map Index',
        accessor: 'sourceMapIndex',
        Cell: ({ cell: { value } }) => (value > -1 ? value : null),
      },
      {
        Header: 'Extra',
        accessor: 'extra',
        disableSortBy: true,
        Cell: CodeCell,
      },
    ],
    [],
  );

  const data = useMemo(
    () => datasetEvents,
    [datasetEvents],
  );

  return (
    <Box mt={3}>
      <Heading size="md">Upstream Dataset Events</Heading>
      <Text>Updates to the upstream datasets since the last dataset-triggered DAG run</Text>
      <Table
        data={data}
        columns={columns}
        isLoading={isLoading}
      />
    </Box>
  );
};

export default UpstreamEvents;
