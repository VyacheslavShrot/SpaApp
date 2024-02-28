#!/bin/bash

celery -A config worker -l INFO -c 2