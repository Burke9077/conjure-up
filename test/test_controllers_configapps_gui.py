#!/usr/bin/env python
#
# tests controllers/configapps/gui.py
#
# Copyright 2016 Canonical, Ltd.


import unittest
from unittest.mock import MagicMock, patch, sentinel

from conjureup import events
from conjureup.consts import cloud_types
from conjureup.controllers.configapps.gui import ConfigAppsController


class ConfigAppsGUIRenderTestCase(unittest.TestCase):

    def setUp(self):
        self.controller = ConfigAppsController()

        self.mock_bundle = MagicMock(name="bundle")
        self.mock_bundle.machines = {"1": sentinel.machine_1}
        self.mock_service_1 = MagicMock(name="s1")
        self.mock_bundle.services = [self.mock_service_1]
        self.finish_patcher = patch(
            'conjureup.controllers.configapps.gui.ConfigAppsController.finish')
        self.mock_finish = self.finish_patcher.start()

        self.view_patcher = patch(
            'conjureup.controllers.configapps.gui.ApplicationListView')
        self.view_patcher.start()
        self.app_patcher = patch(
            'conjureup.controllers.configapps.gui.app')
        self.mock_app = self.app_patcher.start()
        self.mock_app.ui = MagicMock(name="app.ui")
        self.mock_app.juju.current_bundle = self.mock_bundle
        self.mock_app.provider.controller = 'testcontroller'
        self.mock_app.bootstrap.running.exception.return_value = None
        self.ev_app_patcher = patch(
            'conjureup.events.app', self.mock_app)
        self.ev_app_patcher.start()

    def tearDown(self):
        self.finish_patcher.stop()
        self.view_patcher.stop()
        self.app_patcher.stop()
        self.ev_app_patcher.stop()

    def test_connect_maas(self):
        "Call submit to schedule predeploy if we haven't yet"
        self.mock_app.provider.cloud = 'foo'
        self.mock_app.provider.cloud_type = cloud_types.MAAS
        self.controller.connect_maas = MagicMock(return_value=sentinel.maas)
        self.controller.show_app_list()
        self.mock_app.loop.create_task.assert_called_once_with(sentinel.maas)


class ConfigAppsGUIFinishTestCase(unittest.TestCase):

    def setUp(self):
        self.controller = ConfigAppsController()

        self.controllers_patcher = patch(
            'conjureup.controllers.configapps.gui.controllers')
        self.mock_controllers = self.controllers_patcher.start()

        self.controller.render = MagicMock()
        self.controller.render = MagicMock()
        self.app_patcher = patch(
            'conjureup.controllers.configapps.gui.app')
        self.mock_app = self.app_patcher.start()
        self.mock_app.ui = MagicMock(name="app.ui")
        self.ev_app_patcher = patch(
            'conjureup.events.app', self.mock_app)
        self.ev_app_patcher.start()

    def tearDown(self):
        self.controllers_patcher.stop()
        self.app_patcher.stop()
        self.ev_app_patcher.stop()

    def test_show_bootstrap(self):
        "deploy.gui.test_show_bootstrap"
        events.Bootstrapped.clear()
        self.controller.finish()
        self.mock_controllers.use.assert_called_once_with('bootstrap')
