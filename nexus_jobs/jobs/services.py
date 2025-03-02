from django.contrib.postgres.search import SearchQuery, SearchRank
from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import F, Q
from .models import Job

class JobSearchService:
    @staticmethod
    def search_jobs(query, job_type=None, location=None, min_salary=None):
        if not query.strip():
            return Job.objects.none()  # Return empty QuerySet for blank queries

        search_query = SearchQuery(query)

        # Trigram similarity for fuzzy search (title & location)
        title_similarity = TrigramSimilarity("title", query)
        location_similarity = TrigramSimilarity("location", query)

        # Query filtering
        jobs = Job.objects.annotate(
            similarity=title_similarity + location_similarity,  # Fuzzy match score
            rank=SearchRank(F("search_vector"), search_query)  # Full-text search rank
        ).filter(
            Q(search_vector=search_query) |  # Full-text search in description
            Q(title_similarity__gt=0.2) |  # Trigram similarity filter on title
            Q(location_similarity__gt=0.2)   # Trigram similarity filter on location
        )

        # Apply additional filters
        if job_type:
            jobs = jobs.filter(job_type=job_type)
        if location:
            jobs = jobs.filter(location__icontains=location)
        if min_salary:
            jobs = jobs.filter(min_salary__gte=min_salary)

        # Sort results by relevance
        return jobs.order_by("-rank", "-similarity")
