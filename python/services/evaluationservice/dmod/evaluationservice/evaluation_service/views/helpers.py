import io
import zipfile
from wsgiref.util import FileWrapper
from django.views.generic import View

from django.http import HttpResponse
from django.http import HttpRequest
from django.http import JsonResponse
from django.http import HttpResponseBadRequest

import dmod.evaluations.util as evaluation_utilities

import utilities

import writing


class Clean(View):
    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        evaluation_id = request.POST.get("evaluation_id")

        if evaluation_id is None:
            return HttpResponseBadRequest("No evaluation id was passed; nothing can be cleaned")

        channel_name = utilities.get_channel_key(evaluation_id)
        evaluation_key = utilities.get_evaluation_key(evaluation_id)

        response_data = {
            "evaluation": evaluation_id,
            "records_removed": False,
            "errors": list(),
            "messages": list(),
            "removed_files": list()
        }

        connection = utilities.get_redis_connection()
        pipeline = None
        response = None
        status_code = 200

        try:
            if evaluation_key in connection.keys():
                if bool(connection.hget('complete', False)):
                    pipeline = connection.pipeline()
                    pipeline.delete(*list(utilities.get_evaluation_pointers(evaluation_id)))
                    pipeline.publish(channel_name, f"Removed '{evaluation_id}' as requested")
                    pipeline.execute()
                    response_data['records_removed'] = True
                    response_data['messages'].append(f"The '{evaluation_id}' evaluation has been removed")
                else:
                    response_data['messages'].append(f"The '{evaluation_id}' evaluation is still ongoing")
                    status_code = 202
            else:
                message = f"No evaluation named '{evaluation_id}' was found. "\
                          f"Either the wrong key was entered or it was already removed. No records were removed."
                response_data['messages'].append(message)
                status_code = 400
                connection.publish(channel_name, message)
        except Exception as e:
            message = f"{evaluation_id} could not be removed. {str(e)}"
            response_data['messages'].append(message)
            response_data['errors'].append(str(e))
            status_code = 500
        finally:
            if pipeline:
                pipeline.close()

        if status_code < 500:
            try:
                response_data['removed_files'].extend(writing.clean(evaluation_id))
                status_code = 200
            except Exception as e:
                status_code = 500
                response_data['messages'].append(str(e))
                response_data['errors'].append(str(e))

        if not response:
            response = JsonResponse(response_data)

        response.status_code = status_code

        return response


class GetOutput(View):
    def get(self, request: HttpRequest, evaluation_name: str):
        args = {
            key.lower(): value
            for key, value in request.GET.items()
        }
        output_format = args.get("output_format")
        written_data = writing.get_output(evaluation_id=evaluation_name, output_format=output_format)
        file = FileWrapper(io.BytesIO(written_data.get_raw_data()))
        filename = evaluation_utilities.clean_name(evaluation_name) + "." + written_data.get_extension()

        response = HttpResponse(content=file, content_type=written_data.get_content_type())
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
