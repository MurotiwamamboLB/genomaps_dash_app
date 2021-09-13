FROM debian:latest

# bio packages compiled from source or downloaded as binaries will live in the /bio directory
USER root

ENV BIO_DIR=/bio
ENV PATH=$BIO_DIR/bin:$PATH
RUN mkdir -p $BIO_DIR/bin

# environment
ENV HOME /root
WORKDIR $HOME

# install additional packages for prereqs
RUN apt-get update
RUN apt-get install -yq --no-install-recommends build-essential
RUN apt-get install -yq --no-install-recommends wget
RUN apt-get install -yq --no-install-recommends p7zip-full
RUN apt-get install -yq --no-install-recommends zip
RUN apt-get install -yq --no-install-recommends unzip
RUN apt-get install -yq --no-install-recommends curl
RUN apt-get install -yq --no-install-recommends ca-certificates
RUN apt-get install -yq --no-install-recommends locales
RUN apt-get install -yq --no-install-recommends bc
RUN apt-get install -yq --no-install-recommends libglu1-mesa
RUN apt-get install -yq --no-install-recommends csh
RUN apt-get install -yq --no-install-recommends git
RUN apt-get install -yq --no-install-recommends hashdeep
RUN apt-get install -yq --no-install-recommends procps 
RUN apt-get install -yq --no-install-recommends libfontconfig
RUN apt-get install -yq --no-install-recommends libncurses5
RUN apt-get install -yq --no-install-recommends ssh-client
RUN apt-get install -yq --no-install-recommends libxkbcommon-x11-0
RUN apt-get install -yq --no-install-recommends libxcb-xinerama0 



# this has to happen after the apt-gets
RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen
    
# Configure environment
ENV LC_ALL=en_US.UTF-8 \
    LANG=en_US.UTF-8 \
    LANGUAGE=en_US.UTF-8

#RUN wget -O - https://rclone.org/install.sh | bash

#RUN wget https://julialang-s3.julialang.org/bin/linux/x64/1.5/julia-1.5.3-linux-x86_64.tar.gz && \
#	tar -xvzf julia-1.5.3-linux-x86_64.tar.gz -C $BIO_DIR && \
#    rm julia-1.5.3-linux-x86_64.tar.gz

RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
RUN bash Miniconda3-latest-Linux-x86_64.sh -b -p /conda
RUN rm Miniconda3-latest-Linux-x86_64.sh
ENV PATH=/conda/bin:$PATH

##conda packages
RUN pip install dash
RUN pip install jupyter-dash
RUN pip install pandas
RUN pip install simplejson
RUN pip install dash-bootstrap-components

RUN conda install -c conda-forge dash
RUN conda install -c conda-forge dash-core-components
RUN conda install -c conda-forge dash-bootstrap-components
RUN conda install -c plotly plotly
RUN conda install -c conda-forge dash-table
RUN conda install -c menpo pathlib
RUN conda install -c conda-forge pydrive
RUN conda install -c anaconda python-dateutil
RUN conda install -c anaconda requests
#RUN pip install psycopg2
#RUN pip install --upgrade google-cloud-bigquery
#RUN conda install -c anaconda configparser
RUN conda install -c anaconda cryptography
RUN conda install -c r r-essentials
RUN conda install -c r r-base 
RUN conda install -c r r-dplyr
RUN conda install -c r r-ggplot2
RUN conda install -c r r-rjson

#RUN conda install flask
#RUN pip install dash-auth==1.3.2.

RUN conda clean --all -f -y
RUN apt-get update && apt-get install -y gnupg
# gcloud
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] http://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg  add - && apt-get update -y && apt-get install google-cloud-sdk -y

#RUN wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O cloud_sql_proxy
#RUN chmod +x cloud_sql_proxy

#COPY image-annotation-007-ac5c6eb11d0b.json /root
#COPY runfile.sh /root


# Bigquery
#ENV PATH=/root/google-cloud-sdk/bin:$PATH
#COPY dashboard-paradise-69ab99d749d9.json /root
#RUN gcloud auth activate-service-account --key-file image-annotation-007-ac5c6eb11d0b.json
#RUN gcloud auth activate-service-account --key-file dashboard-paradise-69ab99d749d9.json
#RUN gcloud config set project image-annotation-007
#
#RUN runfile.sh    #Check this and change to bigquery?


#COPY getPFU.py ./
#RUN export GOOGLE_APPLICATION_CREDENTIALS="/root/dashboard-paradise-69ab99d749d9.json"



#RUN julia -e 'ENV["GKSwstype"] = "100"; import Pkg; Pkg.update(); pkgs = [ "ArgParse", "Base64", "BioSequences", "BioServices", "DataFrames", "Dates", "DelimitedFiles", "FASTX", "GLM", "HTTP", "JSON", #"MD5", "ProgressMeter", "Random", "Statistics", "StatsPlots", "StatsBase", "uCSV", "PlotlyJS", "CodecZlib", "YAML", "Measures" ]; Pkg.add(pkgs); for pkg in pkgs; eval(Meta.parse("import $pkg")); end; #StatsPlots.plotlyjs()'

ENV HOME /root
WORKDIR $HOME

#RUN mkdir assets
RUN mkdir -p ./.config
ADD .config .config
ADD assets ./
ADD apps ./
COPY *.py ./


RUN mkdir -p .ssh
ADD .ssh .ssh
RUN chmod 400 .ssh/id_ed25519

#COPY *.sh ./
RUN ls -R
RUN git clone git@github.com:MurotiwamamboLB/genomaps_dash_app.git
RUN ls -R
#RUN chmod -R +x cocktail-optimizer-new/Locus-Utilities/tarchive
#COPY phage_table.csv ./
#RUN bash runfile.sh

#RUN julia -e 'import Pkg; LocusJulia_path = "/root/cocktail-optimizer-new/Locus-Utilities/LocusJulia"; push!(LOAD_PATH, LocusJulia_path); Pkg.activate(LocusJulia_path); Pkg.update(); Pkg.instantiate(); #Pkg.activate(); import LocusJulia'

ENTRYPOINT python index.py