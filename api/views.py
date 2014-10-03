from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest

from rest_framework.response import Response
from rest_framework.views import APIView

from contract.models import Contract
from vendor.models import Vendor, Naics, SetAside, SamLoad, Pool
from api.serializers import VendorSerializer, NaicsSerializer, PoolSerializer, ShortVendorSerializer, ContractSerializer, Metadata, MetadataSerializer, ShortPoolSerializer


class GetVendor(APIView):

    def get(self, request, duns, format=None):
        vendor = Vendor.objects.get(duns=duns) 
        return Response(VendorSerializer(vendor).data) 



class ListVendors(APIView):
    
    def get(self, request, format=None):

        try: 
            naics =  Naics.objects.get(short_code=request.QUERY_PARAMS.get('naics'))
            pool = Pool.objects.get(naics=naics)
            setasides = request.QUERY_PARAMS.get('setasides', None)
            if setasides:
                setasides = setasides.split(',')
            
            #check if request is limited by a pool (only used if naics not supplied)

            sam_load_results = SamLoad.objects.all().order_by('-sam_load')[:1]
            sam_load = sam_load_results[0].sam_load if sam_load_results else None

            v_serializer = ShortVendorSerializer(self.get_queryset(pool, setasides), many=True)
            p_serializer = ShortPoolSerializer(pool)

            return  Response({ 'num_results': len(v_serializer.data), 'pool' : p_serializer.data , 'sam_load':sam_load, 'results': v_serializer.data } )

        except Naics.DoesNotExist:
            return HttpResponseBadRequest("You must provide a valid naics code that maps to an OASIS pool")
        #except goes here

    def get_queryset(self, pool, setasides):
        vendors = Vendor.objects.filter(pools=pool)
        if setasides:
            for sa in SetAside.objects.filter(code__in=setasides):
                vendors = vendors.filter(setasides=sa)

        #Also need to filter by vehicle here

        return vendors


class ListNaics(APIView):

    def get(self, request, format=None):
        serializer = NaicsSerializer(self.get_queryset(), many=True)
        return Response({'num_results': len(serializer.data), 'results': serializer.data})

    def get_queryset(self):
        codes = Naics.objects.all()

        #filters
        q = self.request.QUERY_PARAMS.get('q', None)

        if q:
            codes = Naics.objects.filter(description__icontains=q)
        else:
            codes = Naics.objects.all()

        return codes

class ListContracts(APIView):
    
    def get(self, request, format=None):
        contracts = self.get_queryset()

        if contracts == 1:
            return HttpResponseBadRequest("You must provide a vendor DUNS to retrieve contracts.")

        elif not contracts:
            return Response({'num_results': 0, 'results': []})

        else:
            serializer = ContractSerializer(contracts)
            return Response({'num_results': len(serializer.data), 'results': serializer.data})

    def get_queryset(self):
        
        duns = self.request.QUERY_PARAMS.get('duns', None)
        naics = self.request.QUERY_PARAMS.get('naics', None)

        if not duns:
            return 1

        vendor = Vendor.objects.get(duns=duns)
        contracts = Contract.objects.filter(vendor=vendor).order_by('-date_signed')

        if naics:
            #contracts = contracts.filter(NAICS=Naics.objects.filter(code=naics)[0])
            contracts = contracts.filter(NAICS=naics)  #change to above when naics loaded right

        return contracts

class MetadataView(APIView):
    def get(self, request, format=None):
       mds = MetadataSerializer(Metadata())
       return Response(mds.data)
        



