# ImageCutter
A simple Python library intended to be the backend of a FITS Image Cut-Out service. It does support a more typical scripting usage.

## Installation

```
pip install git+https://github.com/jhoar/ImageCutter.git
```

This should install the package and dependencies; on Windows platforms there may be a probelm installing the fitsio package if there is no compiler available, see
https://stackoverflow.com/questions/29376834/how-to-install-the-fitsio-package-in-python

In the longer term this package should migrate to using PyFITS which will resolve this problem

## Usage

### Scripting

```
import ImageCutter

x = ImageCutter()

# open the FITS file
x.prepare('test/test.fits')

# Request a cutout at RA=9.2234028, Dec=-19.421379 to be saved into 'out4.fits' from HDU named 'SCI'. The cut out size is 1.0x1.0 arc minutes in size 
x.fits_cut(9.2234028, -19.421379, 'out1.fits')

# Request a cutout at RA=9.2234028, Dec=-19.421379 to be saved into 'out4.fits' from HDUs named 'SCI' and 'MSK'. The cut out size is 0.6x0.4 arc minutes in size 
x.fits_cut(9.2234028, -19.421379, xs=0.6, ys=0.4, hdu=['SCI','MSK'], 'out2.fits')

# More requests...

# Close file
x.close()
```

### Service backend
Another use directed a service backends is the JSON interface:

```
import ImageCutter

x = ImageCutter()
x.process_json(args.infile, args.outfile)
```
Will read a JSON file with the list of requests for a given source FITS file, and produce a JSON file with the results. Here is an example of a input file:
```
{
	"input":"test/test.fits",
	"request":[
		{
			"req":"req1",
			"ra":"8.80701523121",
			"dec":"-19.434399444444445",
			"xs":"1.0",
			"ys":"1.0",
			"hdu":["SCI"],
			"outfile":"test/outA.fits"
		},
		{
			"req":"req1",
			"ra":"8.80801523121",
			"dec":"-19.434399444444445",
			"outfile":"test/outB.fit"
		}
	]
}
```

The output JSON file is then:

```
{
    "log": [],
    "requests": [
        {
            "log": [
                "OK"
            ],
            "req": "req1",
            "OUTPUT": "test/outA.fits",
            "VOX:Image_Title": "Cutout from test/test.fits",
            "POS_EQ_RA_MAIN": 8.80701523121,
            "POS_EQ_DEC_MAIN": -19.434399444444445,
            "CUTSIZE": [
                0.016666666666666666,
                0.016666666666666666
            ],
            "VOX:Image_Naxes": 2,
            "VOX:Image_Naxis": [
                599,
                599
            ],
            "VOX:Image_Scale": [
                2.777777777778e-05,
                2.777777777778e-05
            ],
            "VOX:Image_Format": "image/fits"
        },
        {
            "log": [
                "OK"
            ],
            "req": "req1",
            "OUTPUT": "test/outB.fit",
            "VOX:Image_Title": "Cutout from test/test.fits",
            "POS_EQ_RA_MAIN": 8.80801523121,
            "POS_EQ_DEC_MAIN": -19.434399444444445,
            "CUTSIZE": [
                0.016666666666666666,
                0.016666666666666666
            ],
            "VOX:Image_Naxes": 2,
            "VOX:Image_Naxis": [
                599,
                599
            ],
            "VOX:Image_Scale": [
                2.777777777778e-05,
                2.777777777778e-05
            ],
            "VOX:Image_Format": "image/fits"
        }
    ],
    "input": "test/test.fits"
}
```
This should be mainly compatible with the IVOA SIA V1 standard for data to be returned in a VOTable from a SIA request.
