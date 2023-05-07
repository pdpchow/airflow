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

import React from "react";
import {
  Box,
  BoxProps,
  Card,
  CardBody,
  CardHeader,
  Heading,
  useTheme,
} from "@chakra-ui/react";
import ReactECharts, { ReactEChartsProps } from "src/components/ReactECharts";
import type { HistoricalMetricsData } from "src/types";
import type { PieSeriesOption } from "echarts";

const formatData = (
  data: HistoricalMetricsData[keyof HistoricalMetricsData]
): [number, PieSeriesOption["data"]] => {
  let sum = 0;
  const formattedData: PieSeriesOption["data"] = [];
  Object.entries(data).forEach(([k, v]) => {
    sum += v;
    formattedData.push({
      name: k,
      value: v,
    });
  });
  return [sum, formattedData];
};

interface Props extends BoxProps {
  title: string;
  data: HistoricalMetricsData[keyof HistoricalMetricsData];
}

const PieChart = ({ title, data, ...rest }: Props) => {
  const theme = useTheme();
  const [sum, formattedData] = formatData(data);
  const option: ReactEChartsProps["option"] = {
    title: {
      text: `on a total of ${sum}`,
      left: "right",
      top: "bottom",
      textStyle: {
        fontSize: "14px",
        color: theme.colors.gray["500"],
      },
    },
    tooltip: {
      trigger: "item",
    },
    legend: {
      left: "center",
      type: "scroll",
    },
    series: [
      {
        name: title,
        type: "pie",
        radius: ["35%", "60%"],
        avoidLabelOverlap: false,
        top: "0%",
        itemStyle: {
          borderRadius: 5,
          borderColor: "#fff",
          borderWidth: 2,
        },
        label: {
          show: false,
          position: "center",
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 16,
            fontWeight: "bold",
          },
        },
        data: formattedData,
      },
    ],
  };

  return (
    <Box {...rest}>
      <Card h="100%">
        <CardHeader textAlign="center" p={3}>
          <Heading size="md">{title}</Heading>
        </CardHeader>
        <CardBody>
          <ReactECharts option={option} />
        </CardBody>
      </Card>
    </Box>
  );
};

export default PieChart;
