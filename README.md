# geos-sim
cadCAD simulation for the Gift Economies of Scale project
status: v0.1

cadCAD: https://github.com/cadCAD-org/cadCAD
latest version of the `geos` work will be made available at: https://github.com/nctzn101/geos-sim/ 

## requirements
To run the simulation several requirements should be installed via `%pip install [PACKAGE_NAME]` (inline in Jupyter) or any other method of your choice. I recommend creating a dedicated environment for installing the required packages and running the simulation via `conda create -n geos python=3.9` and activate it as `conda activate geos`. Installing cadCAD (and the associated requirements) should install most of the dependencies. Other dependencies:

- ipykernel 6.25.2
- plotly 4.11.0
- cadcad 0.4.23
- matplotlib 3.3.0
- networkx 3.2
- numpy 1.26.2
- pandas 2.1.1
- scikit-learn 1.3.2

## run
- please make sure that `geos.py` is within a directory called `module` within the main directory as it is currently imported in the notebook
- run the notebook cells one by one, specifying the parameters in `initial_state_params` and `system_params` 

## todo 
| status | type | description | 
| --- | --- | --- | 
| tbd | feature | resource co-ownership |
| tbd | feature | donation withdrawal |
| tbd | feature | request/donation constraints |
| tbd | feature | waste metrics computation |
| tbd | fix | potential overdonation in last entry in multi-donation strategies |
| tbd | documentation | expand documentation |
| tbd | documentation | list of fixes, features TBD |