from abc import ABC, abstractmethod
from models import EmergencyCase
from sqlalchemy import or_, case


class SearchStrategy(ABC):
    @abstractmethod
    def search(self, query: str, species_filter: str) -> list:
        """
        Execute search query and return a list of EmergencyCase records.
        """
        pass


class KeywordSearchStrategy(SearchStrategy):
    def search(self, query: str, species_filter: str) -> list:
        """
        Keyword search: matches title, description, or keywords.
        """
        db_query = EmergencyCase.query

        # Apply species filter if it's not "All"
        if species_filter and species_filter.lower() != 'all':
            db_query = db_query.filter(
                EmergencyCase.species.ilike(species_filter)
            )

        # Apply keyword/text matching
        if query:
            search_term = f"%{query}%"
            db_query = db_query.filter(
                or_(
                    EmergencyCase.title.ilike(search_term),
                    EmergencyCase.description.ilike(search_term),
                    EmergencyCase.keywords.ilike(search_term)
                )
            )

        return db_query.all()


class SeveritySpeciesSearchStrategy(SearchStrategy):
    def search(self, query: str, species_filter: str) -> list:
        """
        Filters by species and sorts results by severity level:
        Critical -> Moderate -> Minor
        """
        db_query = EmergencyCase.query

        # Apply species filter if it's not "All"
        if species_filter and species_filter.lower() != 'all':
            db_query = db_query.filter(
                EmergencyCase.species.ilike(species_filter)
            )

        # Apply query term filtering if present
        if query:
            search_term = f"%{query}%"
            db_query = db_query.filter(
                or_(
                    EmergencyCase.title.ilike(search_term),
                    EmergencyCase.description.ilike(search_term)
                )
            )

        # Order by severity: Critical (1), Moderate (2), Minor (3)
        severity_order = case(
            (EmergencyCase.severity == 'Critical', 1),
            (EmergencyCase.severity == 'Moderate', 2),
            (EmergencyCase.severity == 'Minor', 3),
            else_=4
        )

        return db_query.order_by(severity_order).all()


class SearchContext:
    def __init__(self, strategy: SearchStrategy | None = None):
        self._strategy = strategy or KeywordSearchStrategy()

    def set_strategy(self, strategy: SearchStrategy):
        self._strategy = strategy

    def execute_search(self, query: str, species_filter: str) -> list:
        return self._strategy.search(query, species_filter)
