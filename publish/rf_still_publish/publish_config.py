# make order to match the func 
# added function will not be listed if not add to checkOrder below ***

precheckOrder = ['check_naming', 'check_group']
publishOrder = ['publish_file', 'publish_image']
publishWipOrder = ['save_file', 'publish_image']
sg_publishOrder = ['publish_version', 'set_task', 'upload_thumbnail', 'upload_media']

modelOrder = ['export_abc', 'export_gpu', 'publish_geo']
rigOrder = ['export_abc', 'export_gpu']
postPublishOrder = ['check_ad', 'summarized_info']

wipPublishOrder = ['save_file', 'publish_image']
wipPostPublistOrder = []
reviewPublishOrder = ['publish_file', 'publish_image']
reviewPostPublistOrder = []

filePublishPreset = {'wip': False, 'rev': False, 'arpv': True}
overridePublishPreset = {'wip': [precheckOrder, wipPublishOrder, sg_publishOrder, wipPostPublistOrder], 
						'rev': [precheckOrder, reviewPublishOrder, sg_publishOrder, reviewPostPublistOrder], 
						'filePublish': [precheckOrder, publishOrder, sg_publishOrder, postPublishOrder]}