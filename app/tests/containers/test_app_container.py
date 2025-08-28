import unittest
from app.containers.app_container import ApplicationContainer
from app.containers.repositories_container import RepositoriesContainer
from app.containers.model_services_container import ModelServicesContainer
from app.containers.pipeline_services_container import PipelineServicesContainer
from app.config.app_config import AppConfig

class TestApplicationContainer(unittest.TestCase):
    def setUp(self):
        self.container = ApplicationContainer()

    def test_app_config(self):
        self.assertIsInstance(self.container.app_config, AppConfig)

    def test_repositories_container(self):
        self.assertIsInstance(self.container._repositories_container, RepositoriesContainer)

    def test_model_services_container_singleton(self):
        msc1 = self.container.model_services_container
        msc2 = self.container.model_services_container
        self.assertIsInstance(msc1, ModelServicesContainer)
        self.assertIs(msc1, msc2)  # Should be singleton

    def test_pipeline_services_container_singleton(self):
        psc1 = self.container.pipeline_services_container
        psc2 = self.container.pipeline_services_container
        self.assertIsInstance(psc1, PipelineServicesContainer)
        self.assertIs(psc1, psc2)  # Should be singleton

    def test_pipeline_services_container_dependencies(self):
        psc = self.container.pipeline_services_container
        self.assertIs(psc.model_services_container, self.container.model_services_container)
        self.assertIs(psc.model_services_container.repositories_container, self.container._repositories_container)

if __name__ == "__main__":
    unittest.main()
