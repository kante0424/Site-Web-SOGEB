from django.http import HttpResponse


def robots_txt(request):
    lines = [
        "User-agent: *",
        "Disallow: /gestion/",
        f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}",
    ]
    return HttpResponse("\n".join(lines) + "\n", content_type="text/plain")
