from injector import inject

from commons.infra.dependency_injection.injectable import injectable
from commons.messaging import BaseEventRouter, Event
from commons.messaging.contracts.events.data_processing_service.models import \
    GeneratedYoutubeContentArticleReadyEvent
from data_collector_service.services.processing.transition_user_collected_content_status_to_processed_service import \
    TransitionUserCollectedContentStatusToProcessedService


@injectable()
class EventRouter(BaseEventRouter):
    """Routes incoming events to the appropriate service logic."""

    @inject
    def __init__(
        self,
        transition_service: TransitionUserCollectedContentStatusToProcessedService,
    ):
        self.transition_service = transition_service

    async def handle_domain_event(self, event: Event):
        """Dispatches the event based on event_type."""
        match event.event_type:
            case GeneratedYoutubeContentArticleReadyEvent.EVENT_TYPE:
                article_ready_event = (
                    GeneratedYoutubeContentArticleReadyEvent.model_validate(
                        event.model_dump()
                    )
                )
                payload = article_ready_event.payload
                print(
                    "🎬 Consuming event ",
                    GeneratedYoutubeContentArticleReadyEvent.EVENT_TYPE,
                    " with external_id: ",
                    payload.external_id,
                )

                await self.transition_service.transition_to_processed(
                    external_id=payload.external_id
                )
                print(
                    "✅ Consumed event ",
                    GeneratedYoutubeContentArticleReadyEvent.EVENT_TYPE,
                    " with external_id: ",
                    payload.external_id,
                )

            case _:
                raise NotImplementedError(
                    f"Event '{event.event_type}' is unimplemented in EventRouter"
                )
