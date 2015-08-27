#+
# Copyright 2014 iXsystems, Inc.
# All rights reserved
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted providing that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
# IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
#####################################################################


from namespace import (Namespace, ConfigNamespace, Command, IndexCommand,
                       description)
from output import output_msg, ValueType
from descriptions import events
from utils import parse_query_args


@description("Prints current Update Train")
class CurrentTrainCommand(Command):
    """
    Usage: current_train

    Displays the current update train.
    """
    def run(self, context, args, kwargs, opargs):
        output_msg(context.connection.call_sync('update.get_current_train'))


@description("Checks for New Updates")
class CheckNowCommand(Command):
    """
    Usge: check_now

    Checks for updates.
    """
    def run(self, context, args, kwargs, opargs):
        output_msg(context.connection.call_sync('update.check'))


@description("Updates the system and reboot it")
class UpdateNowCommand(Command):
    """
    Usage: update_now

    Installs updates if they are available and restarts the system if necessary.
    """
    def run(self, context, args, kwargs, opargs):
        output_msg("System going for an update now...")
        context.submit_task('update.update')


@description("Update configuration namespace")
class UpdateConfigNamespace(ConfigNamespace):
    def __init__(self, name, context):
        super(UpdateConfigNamespace, self).__init__(name, context)
        self.context = context

        self.add_property(
            descr='Current Train',
            name='train',
            get='train',
            type=ValueType.STRING
        )

        self.add_property(
            descr='Auto check',
            name='check_auto',
            get='check_auto',
            type=ValueType.BOOLEAN
        )

        self.add_property(
            descr='Update server',
            name='update_server',
            get='update_server',
        )

    def load(self):
        self.entity = self.context.call_sync('update.get_config')

    def save(self):
        return self.context.submit_task('update.configure', self.entity)


@description("Update namespace")
class UpdateNamespace(Namespace):
    def __init__(self, name, context):
        super(UpdateNamespace, self).__init__(name)
        self.context = context

    def commands(self):
        return {
            '?': IndexCommand(self),
            'current_train': CurrentTrainCommand(),
            # 'check_now': CheckNowCommand(),
            # uncmment above when freenas-pkgtools get updated by sef
            'update_now': UpdateNowCommand(),
        }

    def namespaces(self):
        return [
            UpdateConfigNamespace('config', self.context)
        ]


def _init(context):
    context.attach_namespace('/', UpdateNamespace('update', context))
