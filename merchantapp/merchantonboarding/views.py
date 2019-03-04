from django.shortcuts import render
from django.views.generic import TemplateView
from requests.exceptions import HTTPError
from django.http import HttpResponse
from django.template import loader
import requests
import datetime
from json import dumps, loads

# Create your views here.
class HomePageView(TemplateView):
    def get(self, request, **kwargs):
        return render(request, 'index.html', context=None)

class AcraPageView(TemplateView):
    def get(self, request, **kwargs):
        acra_base_url = "https://data.gov.sg/api/action/datastore_search"
        resource_id = "e8732ea3-adca-4ca0-9fef-2b90c7a24f06"
        query = request.GET.get('uen')
        try:
            response = requests.get(url=acra_base_url,
                                    params={'resource_id': resource_id,
                                            'q': query}
                                    )
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')  # Python 3.6
        except Exception as err:
            print(f'Other error occurred: {err}')  # Python 3.6
        else:
            json_response = response.json()
            records = json_response['result']['records']
            template = loader.get_template('acra.html')
            context = {
                'records_list': records,
            }
            return HttpResponse(template.render(context, request))

class JbpmPageView(TemplateView):
    def get(self, request, **kwargs):
        uen = request.GET.get('uen')
        template = loader.get_template('jbpm.html')
        context = {
            'uen': uen,
        }
        return HttpResponse(template.render(context, request))

class AssessPageView(TemplateView):
    def get(self, request, **kwargs):
        jbpm_base_url = "http://localhost:8080/kie-server/services/rest/server/containers/MerchantOnboarding_1.0.0/processes/MerchantOnboarding.onboardingprocess/instances"
        accept_header = "application/json"
        content_header = "application/json"
        headers = {
                    'Accept': accept_header,
                    'Content-Type': content_header
                   }
        ceo_ic = request.GET.get('ceo_ic')
        uen = request.GET.get('uen')
        net_income = request.GET.get('net_income')
        no_employee = request.GET.get('no_employee')
        found_year = request.GET.get('found_year')
        found_loc = request.GET.get('found_loc')
        total_deposit = request.GET.get('total_deposit')
        vat_id = request.GET.get('vat_id')
        payload = {
                    "merchant": {"com.myspace.merchantonboarding.Merchant": {
                            "ceoIC": ceo_ic,
                            "yearOfEstablishment": found_year,
                            "netIncome": net_income,
                            "numberOfEmployees": no_employee,
                            "registeredLocation": found_loc,
                            "totalDeposit": total_deposit,
                            "uen": uen,
                            "vatID": vat_id
                    }}
                }
        try:
            response = requests.post(url=jbpm_base_url,
                         auth=('wbadmin', 'wbadmin'),
                         headers=headers,
                         json=payload
                         )
            json_response = response.json()
            process_id = dumps(json_response)
            template = loader.get_template('wait.html')
            context = {
                'process_id': process_id,
            }
            return HttpResponse(template.render(context, request))
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')  # Python 3.6
        except Exception as err:
            print(f'Other error occurred: {err}')  # Python 3.6

class CheckCFsPageView(TemplateView):
    def get(self, request, **kwargs):
        try:
            process_id = request.GET.get('process_id')
            query_url = "http://localhost:8080/kie-server/services/rest/server/containers/MerchantOnboarding_1.0.0/processes/instances/" + process_id + "/workitems"
            accept_header = "application/json"
            content_header = "application/json"
            headers = {
                'Accept': accept_header,
                'Content-Type': content_header
            }
            response = requests.get(url=query_url,
                                    auth=('wbadmin', 'wbadmin'),
                                    headers=headers
                                    )
            json_response = response.json()
            cf_operational = json_response['work-item-instance'][0]['work-item-params']['merchant']['com.myspace.merchantonboarding.Merchant']['cfoperational']
            cf_credibility = json_response['work-item-instance'][0]['work-item-params']['merchant']['com.myspace.merchantonboarding.Merchant']['cfcredibility']
            cf_financial = json_response['work-item-instance'][0]['work-item-params']['merchant']['com.myspace.merchantonboarding.Merchant']['cffinancial']
            if cf_credibility:
                cf_credibility = 0.0
            if cf_credibility == -1.0 or cf_operational == -1.0:
                final_cf = -1.0
            elif cf_operational + cf_financial == 0.0:
                final_cf = 0.0
            elif cf_financial < 0.0 and cf_operational < 0.0:
                final_cf = cf_financial + cf_operational + (cf_financial*cf_operational)
            elif cf_financial >= 0.0 and cf_operational >= 0.0:
                final_cf = cf_financial + cf_operational - (cf_financial * cf_operational)
            elif cf_financial*cf_operational < 0.0 and abs(cf_financial) > abs(cf_operational):
                final_cf = (cf_financial + cf_operational)/(1-abs(cf_operational))
            elif cf_financial * cf_operational < 0.0 and abs(cf_financial) < abs(cf_operational):
                final_cf = (cf_financial + cf_operational) / (1 - abs(cf_financial))
            template = loader.get_template('certaintyfactor.html')
            context = {
                'cfoperational': cf_operational,
                'cfcredibility': cf_credibility,
                'cffinancial': cf_financial,
                'cffinal': final_cf,
                'process_id': process_id
            }
            return HttpResponse(template.render(context, request))

        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')  # Python 3.6
        except Exception as err:
            print(f'Other error occurred: {err}')  # Python 3.6

class CheckAssessPageView(TemplateView):
    def get(self, request, **kwargs):
        try:
            process_id = request.GET.get('process_id')
            query_url = "http://localhost:8080/kie-server/services/rest/server/queries/processes/instances/" + process_id + "/variables/instances"
            accept_header = "application/json"
            content_header = "application/json"
            headers = {
                'Accept': accept_header,
                'Content-Type': content_header
            }
            response = requests.get(url=query_url,
                                    auth=('wbadmin', 'wbadmin'),
                                    headers=headers
                                    )
            json_response = response.json()
            result = json_response['variable-instance'][2]['value']
            template = loader.get_template('result.html')
            context = {
                'result': result,
                'process_id': process_id
            }
            return HttpResponse(template.render(context, request))
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')  # Python 3.6
        except Exception as err:
            print(f'Other error occurred: {err}')  # Python 3.6