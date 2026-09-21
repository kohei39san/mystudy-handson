"""Test module to verify diagram generation using OCI template."""

from diagrams.oci import compute, storage, network
from src.generator import generator, save_diagram


def test_oci_template_diagram():
    """
    Test diagram generation using the OCI template.
    
    This test creates a simple OCI architecture diagram using:
    - Compute instances
    - Storage services
    - Network components
    
    The diagram is saved to verify template functionality.
    """
    # Initialize generator with OCI template
    gen = generator(template="src/oci-template.svg")
    
    # Add OCI compute node
    gen.add(compute.VM(label="Web Server"))
    
    # Add OCI storage node
    gen.add(storage.ObjectStorage(label="Object Storage"))
    
    # Add OCI network node
    gen.add(network.Vcn(label="Virtual Cloud Network"))
    
    # Save the generated diagram
    save_diagram(gen, "test_oci_output")
