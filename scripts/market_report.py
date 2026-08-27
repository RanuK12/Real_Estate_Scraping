#!/usr/bin/env python3
"""
Market Report Generator for Real Estate Scraping Project

Generates professional PDF market reports from scraped real estate data.
Includes temporal analysis and professional design.

Author: Emilio Ranucoli
License: MIT
"""

import argparse
import os
import sys
import glob
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
from reportlab.platypus import SimpleDocTemplate