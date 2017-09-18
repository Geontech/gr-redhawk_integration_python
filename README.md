# REDHAWK Integration Python Package

 > **Important:** This project is a part of [gnuradio-redhawk][1] that provides the remaining pieces necessary for integration with REDHAWK.

The REDHAWK Integration Python Package is an OOT module that provides a `redhawk_source` block and a `redhawk_sink` block for data ingress and egress from the Flow Graph, respectively.  Each is intended to replace any data streaming elements that may have been required in the Flow Graph that will be sourced (or sinked) from (or to) a Device in the REDHAWK Domain.  The blocks themselves are CORBA endpoints that are (ultimately) mapped to Ports on a REDHAWK Component using the [gr-component_converter][2].

## Requirements

The supported (i.e., tested) framework versions at this time are:

 1. REDHAWK SDR 2.0.6
 2. GNURadio 3.7.9

## Installation

To install the OOT module, run the `install` make target.

**Source or Package Manager Installations**

```
sudo make install
```

**Pybombs Installations**

```
source <your prefix>/setup_env.sh
make install
```

 > **Note:** Pybombs users do not need to be root to install the integration package since it's likely owned by one's own user.

## Source

The `redhawk_source` block represents an input (Provides) port in REDHAWK.  Using the [converter][2], this block's POA (Portable Object Adapter) is returned by the REDHAWK Component's `getPort` method to bridge the REDHAWK data stream directly into the Flow Graph instance.

### Parameters

| Key | End User | Required | Definition |
| -------- | -------- | -------- | ---------- |
| naming_context_ior | No | Yes | The CORBA Naming Context from the parent Component |
| corba_namespace_name | No | Yes | The CORBA Namespace Name from the parent Component |
| type | Yes | Yes | Block's output port data type for the stream |
| packet_depth | Yes | No | Number of BulkIO packets to allow to queue |

### Special Notes

This block translates the incoming SRI, acquisition timestamp, and other details using [tag_utils](#tag-utils) to create a stream tag.  These tags are then pushed only if the SRI changes (to reduce overhead).  The SRI contains a variety of information related to sample rate, subsize information (if the data is a matrix) as well as units for the data (Hz, seconds, dB, etc.).  Please refer to the [REDHAWK Documentation][3] for details on these structures.

 > **Important Note:** In REDHAWK, every BULKIO Time Stamp is passed with almost no processing cost.  Because we can only pass that structure as a stream tag, which cannot be pushed constantly without a large penalty, the time stamp is only pushed if the SRI's information changes.

## Sink

The `redhawk_sink` block represents an output (Uses) port in REDHAWK.  Using the [converter][2], this block's POA (Portable Object Adapter) is returned by the REDHAWK Component's `getPort` method to bridge the data stream from the Flow Graph back into REDAWK.

### Parameters

| Key | End User | Required | Definition |
| -------- | -------- | -------- | ---------- |
| naming_context_ior | No | Yes | The CORBA Naming Context from the parent Component |
| corba_namespace_name | No | Yes | The CORBA Namespace Name from the parent Component |
| type | Yes | Yes | Block's input port data type for the stream |

### Special Notes

This block **requires** that at least one [stream tag](#tag-utils) has been received to define the number of samples in a packet.  If none is provided the port will never empty the incoming buffer or push a packet.

 > **Important Note:** Because conveying every timestamp change through stream tagging would carry a significant perfomance cost, the time stamp provided by this block to REDHAWK is created at the same time the packet is pushed (i.e., we're re-stamping time).


 > **Important Note:** If no stream tag provides an SRI, the default SRI is used.  This will likely cause problems if there are downstream REDHAWK Components or Devices ingesting the data stream.  Please consider pushing an `rh_packet` with SRI details accurate for your flow graph.


## Tag Utils <span id="tag-utils"></span>

The `redhawk_integration_python` package includes a `tag_utils` module for converting between a REDHAWK Packet and a GNURadio Stream Tag, `rh_packet`.  Any changes in REDHAWK BULKIO packet metadata must be propagated using this tag if the data stream will re-enter REDHAWK by way of a `redhawk_sink`.  Details include the number of samples to include per buffer push, etc. as well as the (important) Signal Related Information (SRI).


[1]: https://github.com/GeonTech/gnuradio-redhawk
[2]: https://github.com/GeonTech/gr-component_converter
[3]: http://redhawksdr.github.io/Documentation/mainch5.html