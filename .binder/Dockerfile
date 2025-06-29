# Use the minimal Jupyter base image (has conda & Python)
FROM jupyter/minimal-notebook:latest

USER root

# Uninstall Jupyter server to prevent Binder trying to run it
RUN pip uninstall -y notebook jupyter_server jupyterlab

USER jovyan

# Copy repo contents into the image
COPY . /home/jovyan/

# Set working directory
WORKDIR /home/jovyan/

# Expose Panel port
EXPOSE 5006

# Start the Panel app directly as the container entrypoint
ENTRYPOINT ["panel", "serve", "data_catalog_app.py", "--address=0.0.0.0", "--port=5006", "--allow-websocket-origin=*"]

