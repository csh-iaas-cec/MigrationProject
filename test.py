import oci
import sys
import time


config = oci.config.from_file(profile_name="informatica-phoenix")
object_storage_client = oci.object_storage.ObjectStorageClient(config)
compute_client = oci.core.ComputeClient(config)

image_ocid = "ocid1.image.oc1.phx.aaaaaaaaeifrif5iwxr4jfrjjj3oij4fejltxac7kowonkhpbtr6ct4dmbca"

get_image_response = compute_client.get_image(image_ocid).data
print(get_image_response)