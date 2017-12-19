from rftool.utils import file_utils
from rftool.utils import sg_process
from rftool.utils import path_info

def list_asset(project='Two_Heroes', assetTypes=['setDress']): 
	listFilter = [["sg_asset_type", "is", a] for a in assetTypes]
	print listFilter
	advancedFilter = {
		        "filter_operator": "any",
		        "filters": listFilter
    			}

	filters = [['project.Project.name', 'is', project], advancedFilter]
	fields = ['sg_asset_type', 'sg_subtype', 'code']
	result = sg_process.sg.find('Asset', filters, fields)
	assets = []

	for entity in result: 
	    asset = path_info.PathInfo(project=project, entity='asset', entitySub1=entity.get('sg_asset_type'), entitySub2=entity.get('sg_subtype'), name=entity.get('code'))
	    assets.append(asset)
	    
	return assets