import importlib
import logging

from apps.common.constants import PALTFORM, CONNECT


class StripeEventDispatcher:
    def __init__(
        self, event_type: str, event_data: dict, connected_account: str = None
    ):
        self.event_type = event_type
        self.event_group = event_type.split(".")[0]
        self.event_data = event_data
        self.account_type = CONNECT if connected_account else PALTFORM

    def dispatch(self):
        event_handler = self.get_handler()
        if event_handler:
            try:
                handler = event_handler(self.event_data)
                handler.handle()
            except Exception as e:
                logging.error(f"Error handling event '{self.event_type}': {str(e)}")

    def get_handler(self):
        module_path = self._get_module_path(self.account_type, self.event_group)
        try:
            handler_module = importlib.import_module(module_path)
            handler_name = self._to_camel_case(self.event_type) + "Handler"
            handler_class = getattr(handler_module, handler_name, None)

            if handler_class:
                return handler_class
            else:
                logging.error(
                    f"Handler class '{handler_name}' not found in module '{module_path}' for {self.account_type} event, {self.event_type}"
                )
                return None

        except AttributeError:
            logging.error(
                f"Failed to find handler '{handler_name}' in module '{module_path}' for {self.account_type} event, {self.event_type}"
            )
            return None

        except ModuleNotFoundError:
            logging.error(
                f"No module found for {self.account_type} event, {self.event_type}"
            )
            return None

    @staticmethod
    def _get_module_path(account_type: str, event_group: str) -> str:
        return (
            f"apps.payments.stripe_events.{account_type}_events.{event_group}_handlers"
        )

    @staticmethod
    def _to_camel_case(event_type: str) -> str:
        components = event_type.replace("_", " ").split(".")
        camel_case_string = "".join(x.title().replace(" ", "") for x in components)
        return camel_case_string
