from libcloud.compute.types import provider
from libcloud.compute.providers import get_driver

auth_username = 'YOUR_USERNAME"
auth_password = "YOUR_PASSWORD"
auth_url = "https://floating_ip:5000"
project_name = "YOUR_PROJECT_NAME or ID"
region_name = "YOUR_REGION_NAME"

provider = get_driver(Provider.OPENSTACK)
conn = provider(auth_username,
                auth_password,
                ex_force_auth_url=auth_url,
                ex_force_auth_version='2.0_password',
                ex_tenant_name=project_name,
                ex_force_service_region=region_name)
                
image = conn.get_image('your_glance_image_id')
flavor = conn.ex_get_size('your_flavor_id')

print('Uploading SSH key pair...')
keypair_name = 'demokey'
pub_key_file = '~/.ssh/id_rsa.pub'
conn.import_key_pair_from_file(keypair_name, pub_keyfile)

print('Creating Security group....')
security_group = conn.ex_create_security_group('allin-one',
                                                'network access application.')
                                                
conn.ex_create_security_group_rule(security_group, 'TCP', 80, 80)
conn.ex_create_security_group_rule(security_group, 'TCP', 22, 22)

print('Spawning instance ...')
userdata = '''#!/usr/bin/env bash
curl -L -s https://git.openstack.org/cgit/stackforge/faafo/plain/contrib/install.sh \
    | bash -s -- -i faafo -i messaging -r api -r worker r demo
'''

testing_instance = conn.create_node(name='all-in-one',
                                    image=image,
                                    size=flavor,
                                    ex_keyname=keypair_name,
                                    ex_userdata=userdata,
                                    exsecurity_groups=[security_group])
                                    
conn.wait_until_running([testing_instance])
pool = conn.ex_list_floating_ip_pools()[0]
floating_ip = pool.create_floating_ip()

print('Allocated new Floating IP from pool : {}'.format(pool))

conn.ex_attach_floating_ip_to_node(testing_instace, floating_ip)

print(' The setup is deployed to http://%s' % floating_ip.ip_address)
