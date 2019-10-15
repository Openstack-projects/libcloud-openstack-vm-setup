#!/usr/bin/python

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
                
images = conn.list_images()
for image in images:
    print(image.id, image.name)
    
flavours = conn.list_sizes()
for flavor in flavors:
    print(flavor.id, flavor.name)
    
image_id = input("Enter the Image ID ")
image = conn.get_image(image_id)
print(image)


print('Uploading SSH key pair...')
keypair_name = 'demokey'
pub_key_file = '~/.ssh/id_rsa.pub'
conn.import_key_pair_from_file(keypair_name, pub_keyfile)

print('Creating Security group....')
all_in_one_security_group = conn.ex_create_security_group('allin-one',
                                                'network access application.')
                                                
conn.ex_create_security_group_rule(security_group, 'TCP', ALL, ALL)
conn.ex_create_security_group_rule(security_group, 'UDP', ALL, ALL)

print('Spawning instance ...')
userdata = '''#!/usr/bin/env bash
curl -L -s https://git.openstack.org/cgit/stackforge/faafo/plain/contrib/install.sh \
    | bash -s -- -i faafo -i messaging -r api -r worker r demo
'''


instance_name = 'all-in-one'
testing_instance = conn.create_node(name='all-in-one',
                                    image=image,
                                    size=flavor,
                                    ex_keyname=keypair_name,
                                    ex_userdata=userdata,
                                    ex_security_groups=[all_in_one_security_group])
                                    
conn.wait_until_running([testing_instance])

print('Checking for unsused Floating IP ...')

unused_floating_ip = None

for floating_ip in conn.ex_list_floating_ips():
    if floating_ip.node_id:
        unused_floatingip = floating_ip
        break
        
if not unused_floating_ip:
    pool = conn.ex_list_floating_ip_pools()[0]
    print('Allocating new floating IP from pool: {}'.format(pool))
    unused_floating_ip = pool.create_floating_ip()
    

conn.ex_attach_floating_ip_to_node(testing_instace, unused_floating_ip)

print(' The setup is deployed to http://%s' % unused_floating_ip.ip_address)
