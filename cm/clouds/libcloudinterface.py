from __future__ import absolute_import
import time
from libcloud.compute.types import Provider as compute_provider
from libcloud.compute.providers import get_driver as compute_get_driver
from libcloud.storage.types import Provider as storage_provider
from libcloud.storage.providers import get_driver as storage_get_driver
import libcloud.security
libcloud.security.VERIFY_SSL_CERT = False

from cm.clouds import CloudInterface
from cm.util.decorators import TestFlag

import logging
log = logging.getLogger('cloudman')


class LibCloudInterface(CloudInterface):

    def __init__(self, app=None):
        super(LibCloudInterface, self).__init__()
        self.app = app
        self.tags_supported = True
        self.update_frequency = 60
        self.public_hostname_updated = time.time()
        self.set_configuration()

    def get_ec2_connection(self):
        """
        Get a reference to the cloud connection object to be used for all
        communication with the cloud for the compute side of resources.
        """
        if not self.ec2_conn:
            try:
                log.debug('Establishing libcloud compute connection using {0} driver.'
                    .format(str(self.app.cloud_type).upper()))
                driver = compute_get_driver(getattr(compute_provider,
                    str(self.app.cloud_type).upper()))
                self.ec2_conn = driver(self.aws_access_key, self.aws_secret_key)
                # Do a simple query to test if provided credentials are valid
                try:
                    self.ec2_conn.list_nodes()
                    log.debug("Got libcloud EC2 connection for region '%s'" %
                              self.ec2_conn.region_name)
                except Exception, e:
                    log.error("Cannot validate provided credentials (A:%s, S:%s): %s"
                              % (self.aws_access_key, self.aws_secret_key, e))
                    self.ec2_conn = None
            except Exception, e:
                log.error("Trouble getting libcloud compute connection: %s" % e)
                self.ec2_conn = None
        return self.ec2_conn

    def get_s3_connection(self):
        """
        Get a reference to the cloud connection object to be used for all
        communication with the cloud for the storage side of resources.
        """
        if not self.s3_conn:
            log.debug('Establishing libcloud storage connection')
            try:
                provider = None
                cloud_type = self.app.cloud_type
                if cloud_type == "ec2":
                    provider = storage_provider.S3
                elif cloud_type.lower() == 'os' or cloud_type.lower() == 'openstack':
                    provider = storage_provider.OPENSTACK_SWIFT
                # elif cloud_type.lower() == 'opennebula':
                #     cloud_interface = ONInterface(app=self.app)
                elif cloud_type == 'dummy':
                    provider = storage_provider.DUMMY

                if provider:
                    log.debug('Establishing libcloud storage connection using {0} provider.'
                        .format(provider))
                    driver = storage_get_driver(provider)
                    self.s3_conn = driver(self.aws_access_key, self.aws_secret_key)
                else:
                    log.error("No storage driver - cannot establish connection "
                        "with storage infrastructure")
            except Exception, e:
                log.error("Trouble getting libcloud storage connection: %s" % e)
                self.s3_conn = None
        return self.s3_conn

    @TestFlag('Local_zone')
    def get_zone(self):
        log.debug("dummy getting zone")

    @TestFlag('ami-l0ca1')
    def get_ami(self):
        log.debug("dummy getting zone")
