from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response

from config.decoratores import validate_input
from config.models import ContentAccessLog, TotalTraffic, ContentSegmentCount, Content
from config.utils import convert_datetime_to_date_hourly, json_to_csv_convertor, two_tuple_to_dic_convertor, \
    traffic_output_validator
from dashboard.serializers import ContentOutputSerializer
from data_control.serializers import GetContentSerializer, ContentManagementOutputSerializer, EditContentSerializer, \
    GetMostVisitedContentSerializer, TopContentSerializer, GetTotalTrafficSerializer, ISPTotalTrafficSerializer, \
    ContentSegmentAccessCountSerializer, ContentSegmentAccessCountOutputSerializer


@validate_input(auth=True, perm='')
def get_all_contents(request, obj: GetContentSerializer):
    query = {}
    if request.data['method'] == 'getContents':
        if obj.search_text:
            query.update({'title': {'$regex': obj.search_text}})
        if obj.provider_id:
            query.update({'provider_id': obj.provider_id})
    elif obj.status:
        query.update({'status': obj.status})
    content_list = Content.list(query).skip(obj.skip).limit(obj.limit)
    if obj.sort:
        content_list = content_list.sort(obj.sort[0], obj.sort[1])
    contents = []
    count = Content.count(query)
    for content in content_list:
        if request.data['method'] == 'getContentsManagement':
            content = ContentManagementOutputSerializer(**content)
        else:
            content = ContentOutputSerializer(**content)
        contents.append(content.dict())
    return Response(data={"detail": contents, "count": count}, status=status.HTTP_200_OK)


@validate_input(auth=True, perm='')
def edit_content(request, obj: EditContentSerializer):
    obj_dict = obj.dict()
    obj_dict.pop('id')
    Content.update_one({'_id': obj.id}, **obj_dict)
    return Response(data={"detail": "content is updated"}, status=status.HTTP_200_OK)


@validate_input(auth=True, perm='')
def get_most_visited_content(request, obj: GetMostVisitedContentSerializer):
    output = []
    time_match, provider_match, content_match = {}, {}, {}
    time_match = {'date_hourly': {'$gt': f'{convert_datetime_to_date_hourly(obj.start_time)}',
                                  '$lt': f'{convert_datetime_to_date_hourly(obj.end_time)}'}}
    if obj.provider_id:
        provider_match = {'provider_id': {'$eq': f'{obj.provider_id}'}}
    if obj.content_name:
        content_match = {'content_id': {'$in': obj.content_name}}
    match_list = [time_match, provider_match, content_match]
    group_list = [{'$group': {'_id': {'content_id': '$content_id'}, 'id': {'$first': '$content_id'},
                              'accessed_bytes': {'$sum': {'$multiply': ['$traffic_factor', f'$accessed_bytes']}}}}]
    contents = ContentAccessLog.aggregate(match_list, group_list, None, None, 'accessed_bytes', obj.skip, obj.limit)
    top_contents = []
    for content in contents:
        content = TopContentSerializer(**content)
        top_contents.append(content.dict())
    output.append(top_contents)

    if obj.get_excel:
        json_to_csv_convertor(top_contents, 'TopContent', *['accessed_bytes', 'id'])
        with open(f'excels/TopContent.csv', 'r') as file:
            response = HttpResponse(file, content_type='csv')
            response['Content-Disposition'] = f'attachment; filename=TopContent.csv'
            return response

    return Response(data={"detail": output}, status=status.HTTP_200_OK)


@validate_input(auth=True, perm='')
def get_total_traffic(request, obj: GetTotalTrafficSerializer):
    output = []
    if obj.provider_id is None and obj.content_id is None:
        traffic_list = TotalTraffic.get_total_traffic(start_time=obj.start_time, end_time=obj.end_time)
    else:
        traffic_list = ContentAccessLog.get_total_traffic(
            start_time=obj.start_time, end_time=obj.end_time, provider_id=obj.provider_id, content_id=obj.content_id)

    for traffic in traffic_list:
        traffic = ISPTotalTrafficSerializer(**traffic)
        output.append(traffic.dict())

    output = traffic_output_validator(output)

    if obj.get_excel:
        excel_records = zip(output[2]['accessed_bytes'], output[1]['accessed_bytes'], output[0]['accessed_bytes'],
                            output[0]['date_hourly'])
        output = two_tuple_to_dic_convertor(('other', 'MTN', 'MCI', 'date_hourly'), list(excel_records))

        json_to_csv_convertor(output, 'TotalTraffic', *['other', 'MTN', 'MCI', 'date_hourly'])
        with open('excels/TotalTraffic.csv', 'r') as file:
            response = HttpResponse(file, content_type='csv')
            response['Content-Disposition'] = f'attachment; filename=TotalTraffic.csv'
            return response

    return Response(data=output, status=status.HTTP_200_OK)


@validate_input(auth=True, perm='')
def get_content_access_count(request, obj: ContentSegmentAccessCountSerializer):
    content_access_count = ContentSegmentCount.list({'content_id': obj.content_id})
    output = []
    for access_count in content_access_count:
        access_count = ContentSegmentAccessCountOutputSerializer(**access_count)
        output.append(access_count.dict())
    if obj.get_excel:
        json_to_csv_convertor(output, 'ContentAccessCount', *['segment', 'access_count'])
        with open('excels/ContentAccessCount.csv', 'r') as file:
            response = HttpResponse(file, content_type='csv')
            response['Content-Disposition'] = f'attachment; filename=ContentAccessCount.csv'
            return response
    return Response(data={"detail": output}, status=status.HTTP_200_OK)
