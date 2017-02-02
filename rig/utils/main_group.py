# Main group module
import maya.cmds as mc
from .. import core as lpc
reload( lpc )


class MainGroup(object):

	def __init__(self, assetName=''):

		# Groups
		self.Asset_Grp = lpc.Null()
		self.Ctrl_Grp = lpc.Null()
		self.Still_Grp = lpc.Null()
		self.Jnt_Grp = lpc.Null()
		self.Skin_Grp = lpc.Null()
		self.Ikh_Grp = lpc.Null()
		self.Geo_Grp = lpc.Null()
		self.Geo_Md = lpc.Null()
		self.Geo_Lo = lpc.Null()
		self.Geo_Hi = lpc.Null()


		if assetName:
			self.Asset_Grp.name = '%s%s_Grp' % (assetName[0].upper(), assetName[1:])
		else:
			self.Asset_Grp.name = 'Asset_Grp'

		self.Still_Grp.name = 'Still_Grp'
		self.Ctrl_Grp.name = 'Ctrl_Grp'
		self.Jnt_Grp.name = 'Jnt_Grp'
		self.Skin_Grp.name = 'Skin_Grp'
		self.Ikh_Grp.name = 'Ikh_Grp'
		self.Geo_Grp.name = 'Geo_Grp'
		self.Geo_Md.name = 'Md_Geo_Grp'
		self.Geo_Hi.name = 'Hi_Geo_Grp'
		self.Geo_Lo.name = 'Lo_Geo_Grp'


		self.Asset_Grp.lockHideAttrs('tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz')
		self.Ctrl_Grp.lockHideAttrs('tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz')
		self.Still_Grp.lockHideAttrs('tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz')
		self.Jnt_Grp.lockHideAttrs('tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz')
		self.Skin_Grp.lockHideAttrs('tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz')
		self.Ikh_Grp.lockHideAttrs('tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz')


		# Place_Ctrl
		self.Place_Ctrl = lpc.Control('crossArrow')
		self.Place_Ctrl.name = 'Place_Ctrl'
		self.Place_Ctrl.color = 'yellow'
		self.Place_Ctrl.attr('sy') >> self.Place_Ctrl.attr('sx')
		self.Place_Ctrl.attr('sy') >> self.Place_Ctrl.attr('sz')
		self.Place_Ctrl.lockHideAttrs('v', 'sx', 'sz')

		# Offset_Ctrl
		self.Offset_Ctrl = lpc.Control('circle')
		self.Offset_Ctrl.name = 'Offset_Ctrl'
		self.Offset_Ctrl.color = 'yellow'
		self.Offset_Ctrl.lockHideAttrs('v', 'sx', 'sy', 'sz')

		# Parenting
		self.Place_Ctrl.parent(self.Asset_Grp)
		self.Still_Grp.parent(self.Asset_Grp)
		self.Geo_Grp.parent(self.Asset_Grp)

		self.Offset_Ctrl.parent(self.Place_Ctrl)

		self.Ctrl_Grp.parent(self.Offset_Ctrl)
		self.Jnt_Grp.parent(self.Offset_Ctrl)
		self.Skin_Grp.parent(self.Offset_Ctrl)
		self.Ikh_Grp.parent(self.Offset_Ctrl)

		self.Geo_Md.parent(self.Geo_Grp)
		self.Geo_Hi.parent(self.Geo_Grp)
		self.Geo_Lo.parent(self.Geo_Grp)

		# constraint
		mc.parentConstraint(self.Offset_Ctrl, self.Geo_Grp, mo=True)
		mc.scaleConstraint(self.Offset_Ctrl, self.Geo_Grp)

		# Set default attributes
		self.Jnt_Grp.attr('v').v = 0
		self.Ikh_Grp.attr('v').v = 0
		self.Still_Grp.attr('v').v = 0