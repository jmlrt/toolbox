#!/bin/bash

# This script requires ghostscript
# Reference: https://gist.github.com/firstdoit/6390547

case $1 in
	1) PDF_SETTINGS="/screen";;
	2) PDF_SETTINGS="/ebook";;
	3) PDF_SETTINGS="/printer";;
	4) PDF_SETTINGS="/prepress";;
	5) PDF_SETTINGS="/default";;
	*) exit 1
esac

case $2 in
	color)		COLOR_SETTINGS="";;
	grayscale)	COLOR_SETTINGS="-dColorConversionStrategy=/Gray -dProcessColorModel=/DeviceGray";;
	*) 		exit 1
esac

FILE_NAME=${3%.pdf}

gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=$PDF_SETTINGS "$COLOR_SETTINGS" -dNOPAUSE -dQUIET -dBATCH -sOutputFile="${FILE_NAME}-lite.pdf" "${FILE_NAME}.pdf"
