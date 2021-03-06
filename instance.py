import oci
import sys
import time


config = oci.config.from_file(profile_name="informatica-phoenix")
object_storage_client = oci.object_storage.ObjectStorageClient(config)
compute_client = oci.core.ComputeClient(config)

#### Comments

object_name = sys.argv[1]
version = "server 2008 r2 enterprise"
os = "Windows"

####
compartment_id = "ocid1.compartment.oc1..aaaaaaaaeyztjbsz5yaonksmqzsb7xy6sukjrxai452ciraf7bdhu7tcceqa"
availability_domain = "KTpF:PHX-AD-1"
shape="VM.Standard2.2"
subnet_id = "ocid1.subnet.oc1.phx.aaaaaaaaclknrqxvpct2zrnsxahrct5nptxvcv5avxckxwk6qe5rvpdism5a"

custom_version = dict()

custom_version["os"] = os
custom_version["version"] = version


#######################Creation of image############################
def create_image(object_name, version):
	source_image_type="QCOW2"
	object_storage_uri = "https://objectstorage.us-phoenix-1.oraclecloud.com/n/idnsgznaeqlg/b/RavelloMigration/o/"+object_name
	source_type="objectStorageUri"
	image_source_details = oci.core.models.ImageSourceViaObjectStorageUriDetails(source_image_type = source_image_type,
		source_type = source_type,
		source_uri = object_storage_uri,
		operating_system = version["os"],
		operating_system_version= version["version"])

	tags = dict()
	tags["BLUEPRINT"] = object_name[:-6]
	create_image_details = oci.core.models.CreateImageDetails(compartment_id = compartment_id, 
		image_source_details = image_source_details, 
		launch_mode = "PARAVIRTUALIZED",
		display_name = object_name[:-6]+"_new",
		freeform_tags = tags)

	image_details = compute_client.create_image(create_image_details).data
	image_ocid = image_details.id
	get_image_response = compute_client.get_image(image_ocid)
	wait_until_image_available_response = oci.wait_until(compute_client, get_image_response, 'lifecycle_state', 'AVAILABLE', max_wait_seconds=4800)
	print(wait_until_image_available_response.data)
	create_instance(image_ocid)


##################Creation of instance ############################

def create_instance(image_ocid):
	get_image_response = compute_client.get_image(image_ocid).data
	image_name = get_image_response.display_name
	instance_source_details = oci.core.models.InstanceSourceViaImageDetails(source_type = "image", image_id = image_ocid)
	instance_launch_options = oci.core.models.LaunchOptions(boot_volume_type = "PARAVIRTUALIZED", network_type = "PARAVIRTUALIZED")

	launch_instance_details = oci.core.models.LaunchInstanceDetails(availability_domain = availability_domain,
		compartment_id = compartment_id,
		display_name = image_name,
		subnet_id = subnet_id,
		shape = shape,
		source_details = instance_source_details,
		launch_options = instance_launch_options)
	# compute_client.launch_instance(launch_instance_details = launch_instance_details)
	# print("Creating instance "+ image_name)
	# time.sleep(10)
	instance_details = compute_client.launch_instance(launch_instance_details = launch_instance_details)
	instance_id = instance_details.data.id
	get_instance_response = compute_client.get_instance(instance_id)
	wait_until_instance_available_response = oci.wait_until(compute_client, get_instance_response, 'lifecycle_state', 'RUNNING', max_wait_seconds=4800)
	print(wait_until_instance_available_response.data)


create_image(object_name, custom_version)
