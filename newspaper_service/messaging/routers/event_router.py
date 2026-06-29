from injector import inject
from pydantic import ValidationError

from commons.infra.dependency_injection.injectable import injectable
from commons.messaging import BaseEventRouter, Event
from commons.messaging.contracts.events.data_collector_service.models import \
    UserCollectedContentReadyToBeUsedEvent
from newspaper_service.services.consider_article_candidate.consider_user_collected_content_article_candidate_service import \
    ConsiderUserCollectedContentArticleCandidateService


@injectable()
class EventRouter(BaseEventRouter):
    @inject
    def __init__(
        self,
        consider_article_candidate_service: ConsiderUserCollectedContentArticleCandidateService,
    ):
        self.consider_user_collected_content_article_candidate_service = (
            consider_article_candidate_service
        )

    async def handle_domain_event(self, event: Event):
        try:
            match event.event_type:
                case UserCollectedContentReadyToBeUsedEvent.EVENT_TYPE:
                    ready_event = UserCollectedContentReadyToBeUsedEvent(
                        **event.model_dump()
                    )
                    await self.consider_user_collected_content_article_candidate_service.consider_candidate(
                        user_id=ready_event.payload.user_id,
                        user_collected_content_id=ready_event.payload.user_collected_content_id,
                    )
                case _:
                    raise NotImplementedError(f"Unknown event type: {event.event_type}")
        except ValidationError as e:
            print(f"❌ [EventRouter] Validation error for '{event.event_type}': {e}")
            raise
        except NotImplementedError as e:
            print(
                f"❌ [EventRouter] Not implemented error for '{event.event_type}': {e}"
            )
            raise
        except Exception as e:
            print(f"❌ [EventRouter] Error handling '{event.event_type}': {e}")
            raise
