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

import { defaultFormatWithTZ } from '../../../../../datetime_utils';

/* global moment */

export const LogLevel = {
  DEBUG: 'DEBUG',
  INFO: 'INFO',
  WARNING: 'WARNING',
  ERROR: 'ERROR',
  CRITICAL: 'CRITICAL',
};

export const parseLogs = (data, timezone, logLevelFilter, logGroupFilter) => {
  const lines = data.split('\n');

  if (!data) {
    return {};
  }

  const parsedLines = [];
  const logGroups = new Set();

  lines.forEach((line) => {
    let parsedLine = line;

    // Apply log level filter.
    if (logLevelFilter && !line.includes(logLevelFilter)) {
      return;
    }

    const regExp = /\[(.*?)\] \{(.*?)\}/;
    const matches = line.match(regExp);
    if (matches) {
      // Replace UTC with the local timezone.
      const dateTime = matches[1];
      const logGroup = matches[2].split(':')[0];
      if (dateTime && timezone) {
        const localDateTime = moment(dateTime).tz(timezone).format(defaultFormatWithTZ);
        parsedLine = line.replace(dateTime, localDateTime);
      }

      logGroups.add(logGroup);

      // Apply the log group filter.
      if (logGroupFilter && logGroup !== logGroupFilter) {
        return;
      }
    }

    parsedLines.push(parsedLine);
  });

  return { parsedLogs: parsedLines.join('\n'), logGroups: Array.from(logGroups).sort() };
};
