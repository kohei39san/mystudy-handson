FROM fnproject/python:3.9-dev as build-stage
WORKDIR /function
ADD scripts/requirements.txt /function/
RUN pip3 install --target /python/ --no-cache --no-cache-dir -r requirements.txt

FROM fnproject/python:3.9
WORKDIR /function
COPY --from=build-stage /python /python
ADD scripts/ /function/
RUN rm -fr ~/.cache/pip /tmp* requirements.txt func.yaml Dockerfile*
ENV PYTHONPATH=/python
ENTRYPOINT ["/python/bin/fdk", "/function/func.py", "handler"]