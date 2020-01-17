from django.shortcuts import render

from rest_framework.views import APIView
from django.views.generic import View

from django.http import JsonResponse

import requests
from json.decoder import JSONDecodeError


# Create your views here.
class ElasticsearchRestApiProxyView(View):

    def get(self, request, **kwargs):

        # only admin can query elasticsearch proxy at this point
        if not request.user.is_superuser:
            return JsonResponse({
                'message': 'no permission'
            }, status=405)

        # strip prefixed "/search/es-proxy" in route path
        subpath = request.path[16:]
        if subpath[0] == '/':
            subpath = subpath[1:]
        
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json'
        }
        res = requests.get(f'http://localhost:9200/{subpath}', headers=headers, params=request.GET)

        if res.status_code == 200:
            try:
                es_res_data = {
                    'elasticsearch-json-data': res.json()
                }
            except JSONDecodeError:
                es_res_data = {
                    'elasticsearch-non-json-data': res.text
                }
        else:
            es_res_data = {
                'elasticsearch-non-json-data': res.text
            }

        return JsonResponse(es_res_data)
