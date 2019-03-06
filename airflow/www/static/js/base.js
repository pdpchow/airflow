/**
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements. See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership. The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License. You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */

import { defaultFormatWithTZ, formatDateStr, moment } from './datetime-utils';


const getSelectedTimeZone = () => {
  return $('#clock').data('selected-tz')
};

export const formatInSelectedTz = (dateString) => {
  let tz = getSelectedTimeZone();
  return formatDateStr(dateString, tz);
};

function displayTime() {
  let $clock = $('#clock');
  let tz = $clock.data('selected-tz');
  $clock
    .attr("data-original-title", function() {
      return hostName
    })
    .text(moment().tz(tz).format(defaultFormatWithTZ));

  setTimeout(displayTime, 1000);
}

$(document).ready(function () {
  $("#tz-picker li").click(function(e) {
    let tz = $(this).text() == 'Local' ? moment.tz.guess() : 'UTC';
    $('.tz-aware').each(function() {
      $(this).trigger('tz-changed', tz);
    })
  });

  $('#clock').on('tz-changed', function(event, tz) {
    $(this).data('selected-tz', tz);
    displayTime();
  });

  // Initialize default time zone and start clock
  $('.tz-aware').each(function() {
    $(this).trigger('tz-changed', 'UTC');
  })

  $('span').tooltip();
  $.ajaxSetup({
    beforeSend: function(xhr, settings) {
      if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
        xhr.setRequestHeader("X-CSRFToken", csrfToken);
      }
    }
  });
});
