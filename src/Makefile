COMPILER=g++
INCLUDES=`pkg-config --cflags glib-2.0 gstreamer-1.0 cairo`
LIBS=`pkg-config --libs glib-2.0 gstreamer-1.0 cairo` -lgstvideo-1.0

#remember that all makefile targets are in the form:
#<target>: <dependency> <dependency> <dependency>
#<tab>--><command(s) to make target>

#special variable $@ contains the target name.

all: relay_stream relay_stream_with_overlay json_rpc_server_test json_rpc_client_test

clean:
	rm relay_stream
	rm relay_stream_with_overlay
	rm json_rpc_server_test
	rm json_rpc_client_test

relay_stream:
	$(COMPILER) `pkg-config --cflags glib-2.0 gstreamer-1.0` $@.c `pkg-config --libs glib-2.0 gstreamer-1.0` -o $@	

relay_stream_with_overlay:
	$(COMPILER) $(INCLUDES) $@.c $(LIBS) -o $@

json_rpc_server_test: abstractrpcstubserver.h
	g++ $@.cpp -ljsonrpc -o $@

json_rpc_client_test: abstractrpcstubserver.h
	g++ $@.cpp -ljsonrpc -o $@

abstractrpcstubserver.h: rpcstubclient.h
	jsonrpcstub -s -o ./ rpc_spec.json RPCSpecStub

rpcstubclient.h: rpc_spec.json
	jsonrpcstub -c -o ./ rpc_spec.json RPCSpecStub 
