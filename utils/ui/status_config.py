import sys
import os

moduleDir = os.path.dirname(sys.modules[__name__].__file__)

statusOrder = ['wtg', 'rdy', 'ip', 'wip', 'rev', 'pub', 'fix', 'hld', 'apr', 'p_apr']
statusMap = {'wtg': {'display': 'Waiting to Start', 'icon': '%s/_sgicons/wtg_icon.png' % moduleDir},
			'rdy': {'display': 'Ready to Start', 'icon': '%s/_sgicons/rdy_icon.png' % moduleDir},
			'ip': {'display': 'In progress', 'icon': '%s/_sgicons/ip_icon.png' % moduleDir},
			'rev': {'display': 'Pending Review', 'icon': '%s/_sgicons/review_icon.png' % moduleDir},
			'pub': {'display': 'Pending for Publish', 'icon': '%s/_sgicons/pub_icon.png' % moduleDir},
			'fix': {'display': 'Fix', 'icon': '%s/_sgicons/fix_icon.png' % moduleDir},
			'hld': {'display': 'On Hold', 'icon': '%s/_sgicons/hld_icon.png' % moduleDir},
			'apr': {'display': 'Approved', 'icon': '%s/_sgicons/apr_icon.png' % moduleDir},
			'p_apr': {'display': 'Pending Approve', 'icon': '%s/_sgicons/p_aprv_icon.png' % moduleDir}, 
			'wip': {'display': 'Work in Progress', 'icon': '%s/_sgicons/wip_icon.png' % moduleDir}
			}

publishStatuses = ['wip', 'rev', 'p_apr', 'apr']

# process
stepLimit = {'Asset': ['Design', 'Model', 'Rig', 'Shader', 'Texture'],
			'Shot': ['Layout', 'Animation', 'FX', 'Comp', 'Light']}