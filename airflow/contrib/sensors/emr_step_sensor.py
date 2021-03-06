# -*- coding: utf-8 -*-
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
from airflow.contrib.hooks.emr_hook import EmrHook
from airflow.contrib.sensors.emr_base_sensor import EmrBaseSensor
from airflow.utils.decorators import apply_defaults


class EmrStepSensor(EmrBaseSensor):
    """
    Asks for the state of the step until it reaches a terminal state.
    If it fails the sensor errors, failing the task.

    :param job_flow_id: job_flow_id which contains the step check the state of
    :type job_flow_id: string
    :param step_id: step to check the state of
    :type step_id: string
    """

    NON_TERMINAL_STATES = ['PENDING', 'RUNNING', 'CONTINUE']
    FAILED_STATE = ['CANCELLED', 'FAILED']
    template_fields = ['job_flow_id', 'step_id']
    template_ext = ()

    @apply_defaults
    def __init__(self,
                 job_flow_id,
                 step_id,
                 *args,
                 **kwargs):
        super(EmrStepSensor, self).__init__(*args, **kwargs)
        self.job_flow_id = job_flow_id
        self.step_id = step_id

    def get_emr_response(self):
        emr = EmrHook(aws_conn_id=self.aws_conn_id).get_conn()

        self.log.info('Poking step %s on cluster %s', self.step_id, self.job_flow_id)
        return emr.describe_step(ClusterId=self.job_flow_id, StepId=self.step_id)

    @staticmethod
    def state_from_response(response):
        return response['Step']['Status']['State']
