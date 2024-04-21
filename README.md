# Isochrones

In lieu of writing up a while readme right now, here is the content of the last PR, which is where most of the work on this kicks off.

https://github.com/bopo16/isochrones/pull/1#issue-2254920652

> Using TravelTime SDK for python, created functionality to request a range of isochrones and plot them on a map.  
Also refined plotting of roads and boundary polygon, and added a point feature for destination (eg. Central Station).  
This is all handled in `plot_data.py`    
> 
> Separated downloading functionality into its own file - `download_data.py`. This may be better suited as a Jupyter notebook, to better separate plotting/loading functions, and would allow the user to selectively run cells depending on whether or not data needs to be downloaded using `osmnx` or not.
> 
> Created a similar version of `download_data.py` called `download_data_small.py`, which does the exact same thing but with a smaller network dataset (in this case, Parramatta, NSW). There is almost certainly a better way to do this, but for now it works pretty well for quickly iterating when testing stuff.
> 
> Begun work on incorporating the request(s) to TravelTime API as POST requests in a separate `requests.p`y file. This allows a bit more customisation compared to the Python SDK, and allows multiple isochrones to be requested at once. Not that I'm likely to get rate limited, but it does seem like the right path forward. I'm not really in the mood to copy the request for each iteration of travel_time, so it would be great to generate the json with [apple/pkl](https://github.com/apple/pkl) at some point.
> 
> The other thing I'd like to do is download the isochrones to disk once I've configured them in a way I like so I can start working on the in GIS software. Could be good to add this if I shove this whole thing into a Jupyter notebook for others to use at some point.
> 
> Also messed around with `mapping.ipynb`, for testing quick stuff and getting parameters, etc.  
May remove `isochrones.py` in future updates, as it's kind of a stub, with `plot_data.py` superseding it.
> 
> Also made minor additions to `requirements.txt` and `.gitignore`
