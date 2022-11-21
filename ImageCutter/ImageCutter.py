#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import warnings
warnings.filterwarnings('ignore')

import argparse
import json
from typing import List, Dict

import fitsio
import numpy
from astropy import wcs



"""
Created on Mon Feb 19 07:05:54 2018

@author: johnhoar

Lightly massaged from the DESCUT program: https://github.com/mgckind/descut, see LICENSE

"""

class FITSImageCutter:
    
    infile: str
    fits_file: fitsio.FITS
    output: Dict = {'log':[], 'requests':[]}
        
    def prepare(self, infile: str):
        try:
            self.output['input'] = infile
            self.infile = infile
            self.fits_file = fitsio.FITS(infile, 'r')
        except Exception as err:
            self.output['log'].append('Error! {}'.format(err))
            raise
        
    def close(self):
        try:
            self.fits_file.close()
        except Exception as err:
            self.output['log'].append('Error! {}'.format(err))
 
    def fits_cutkw(self, **kwargs):
        ra = float(kwargs['ra'])
        dec = float(kwargs['dec'])
        out = kwargs['outfile']

        if 'req' in kwargs:
            req = kwargs['req']
        else: 
            req = 'REQ'

        if 'xs' in kwargs:
            xs = float(kwargs['xs'])
        else: 
            xs = 1.0

        if 'ys' in kwargs:
            ys = float(kwargs['ys'])
        else: 
            ys = 1.0

        if 'ext' in kwargs:
            hdu = kwargs['hdu']
        else: 
            hdu = ['SCI']

        self.fits_cut(ra, dec, out, req=req, xs=xs, ys=ys, hdu=hdu)        

    # cut function for individual exposure
    def fits_cut(self, ra: float, dec: float, outfile: str, \
                 req: str='REQ', xs: float = 1.0, ys: float = 1.0, hdu: List[str] = ['SCI']):
    
        # Initialise output dict
        req_output = {'log':[], 'req':req}
        
        # Get the header
        try:
            # We get the WCS info from the first extension in the list
            header = self.fits_file[0].read_header()
        except Exception as err:
            req_output['log'].append('Error! {}'.format(err))
            raise
            
        # Read in the WCS with astropy wcs
        try:
            image_wcs = wcs.WCS(header)
        except Exception as err:
            req_output['log'].append('Error! {}'.format(err))
            raise
        
        # Get the pixel-scale of the input image
        scale = wcs.utils.proj_plane_pixel_scales(image_wcs)
        x_scale = scale[0].tolist() * 3600
        y_scale = scale[1].tolist() * 3600
    
        # Define the geometry of the thumbnail
        x0, y0 = image_wcs.wcs_world2pix(ra, dec, 0)
        x0 = round(x0.tolist())
        y0 = round(y0.tolist())
    
        dx = int(0.5 * xs * 60 / x_scale)
        dy = int(0.5 * ys * 60 / y_scale)
    
        naxis1 = 2 * dx + 1
        naxis2 = 2 * dy + 1
        y1 = y0 - dy
        y2 = y0 + dy + 1
        x1 = x0 - dx
        x2 = x0 + dx +1
    
        if y1 < 0:
            y1 = 0
            # if at edge, set x0+1 as crpix1
            dy = y0
        if x1 < 0:
            x1 = 0
            # if at edge, set y0+1 as crpix2
            dx = x0

        try:
            ofits = fitsio.FITS(outfile, 'rw', clobber=True)
        except Exception as err:
            req_output['log'].append('Error! {}'.format(err))
            raise
    
        # For each extension
        for ext in hdu:
            
            # Read the extension header
            hdr = self.fits_file[0].read_header()
            
            # Create a canvas
            image = numpy.zeros((naxis1, naxis2))
        
            # Read in the image section we want for SCI/WGT/MSK
            image = self.fits_file[0][y1:y2, x1:x2]
        
            # make deepcopy of orginal header
            new_header = wcs.WCS.deepcopy(hdr)
        
            # update the copy as a new headers
            new_header['CRPIX1'] = hdr['CRPIX1'] - x0 + dx + 1
            new_header['CRPIX2'] = hdr['CRPIX2'] - y0 + dy + 1
        
            # add new cutout center to new header
            new_header['RA_CUT'] = ra
            new_header['DEC_CUT'] = dec
            
            # Write extension
            ofits.write(image, header=new_header, extname='')
                        
            req_output['OUTPUT'] = outfile            

            # Bunch of keywords which the SIA V1 Spec requires
            req_output['VOX:Image_Title'] = 'Cutout from {}'.format(self.infile) #Can't think of anything better here
            req_output['POS_EQ_RA_MAIN'] = ra # Ditto
            req_output['POS_EQ_DEC_MAIN'] = dec # Ditto
            req_output['CUTSIZE'] = [xs / 60, ys / 60] # degrees           
            req_output['VOX:Image_Naxes'] = 2
            req_output['VOX:Image_Naxis'] = [naxis1, naxis2]
            req_output['VOX:Image_Scale'] = [scale[0].tolist(), scale[1].tolist()]
            req_output['VOX:Image_Format'] = 'image/fits'

        # Write out the file
        try:
            ofits.close()
        except Exception as err:
            req_output['log'].append('Error! {}'.format(err))
            raise
        
        req_output['log'].append('OK')
        self.output['requests'].append(req_output)
        

    def process_json(self, infile: str, outfile: str):
          
        # Open input and output file
        with open(infile) as datafile:    
            data = json.load(datafile)
        
        # Open file
        inputFile = data['input']
        
        if inputFile is None:
            self.output['log'].append('Error! No input FITS file from JSON')
            return
        
        try:
            self.prepare(inputFile)
            # For each record
            for reqs in data['request']:
                self.fits_cutkw(**reqs)

        except Exception:
            self.output['log'].append('Error! Processing failed')
            
        else:
            # Close file
            self.close()
        
        # Return log
        with open(outfile, 'w') as ofile:
            json.dump(self.output, ofile, indent=4)
    
    
def test():
    print('Test 0')
    
    x = FITSImageCutter()

    # Test not opened file yet
    print('Test 1')
    try:
        x.fits_cut(req='Test 1', ra=8.80701523121, dec=-19.434399444444445,outfile='out1.fits')
    except Exception as err:
        print('Failed as expected: {}'.format(err))
    
    # Test missing file
    print('Test 2')
    try:
        x.prepare('Nothing.fits')
    except Exception as err:
        print('Failed as expected: {}'.format(err))
    
    # Normal case, open file
    print('Test 3')
    x.prepare('test/test.fits')
    
    # Test wrong HDU
    print('Test 4')
    try:
        x.fits_cut(req='Test 2', ra=8.80701523121, dec=-19.434399444444445, xs=1.0, ys=1.0, hdu=['NOTHERE'], outfile='out1.fits')
    except Exception as err:
        print('Failed as expected: {}'.format(err))
   
    # Normal case
    print('Test 5')
    x.fits_cut(req='Test 3', ra=8.80701523121, dec=-19.434399444444445, xs=1.0, ys=1.0, hdu=['SCI'], outfile='out1.fits')
    
    # Rectangle shape
    print('Test 6')
    x.fits_cut(req='Test 4', ra=8.80702523121, dec=-19.434399444444445, xs=0.5, ys=1.0, hdu=['SCI'], outfile='out2.fits')
    
    # Smaller square
    print('Test 7')
    d = { 'req':'Test 5', 'ra':8.80703523121, 'dec':-19.434399444444445, 'outfile':'out3.fits'}
    
    x.fits_cutkw(**d)
    
    # On the edge, do not use keywords
    print('Test 8')
    x.fits_cut(9.2234028, -19.421379, 'out4.fits')
        
    # Close the file
    print('Test 10')
    d = x.close()
    print(d)
    
    # Test reading closed file
    print('Test 11')
    try:
        x.fits_cut('Test 7', 9.2234028, -19.421379, 1.0, 1.0, 'SCI', 'out6.fits')
    except Exception as err:
        print('Failed as expected: {}'.format(err))
   
if __name__ == "__main__":

    cutter = FITSImageCutter()
    
#    test()
    
    parser = argparse.ArgumentParser(description = 'ImageCutter')
    parser.add_argument('infile', help='Input JSON file')
    parser.add_argument('outfile', help='Output JSON file')
#    args = parser.parse_args()
#    cutter.process_json(args.infile, args.outfile)

    cutter.process_json('test/input.json', 'test/out.json')
