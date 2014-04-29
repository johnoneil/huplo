COMPILER=g++
INCLUDES=`pkg-config --cflags glib-2.0 gstreamer-1.0 cairo`
LIBS=`pkg-config --libs glib-2.0 gstreamer-1.0 cairo` -lgstvideo-1.0
FLAGS=-std=c++11

#remember that all makefile targets are in the form:
#<target>: <dependency> <dependency> <dependency>
#<tab>--><command(s) to make target>

#special variable $@ contains the target name.

all: relay_stream relay_stream_with_overlay json_rpc_server_test json_rpc_client_test json_rpc_relay

clean:
	rm relay_stream
	rm relay_stream_with_overlay
	rm json_rpc_server_test
	rm json_rpc_client_test
	rm json_rpc_relay

relay_stream:
	$(COMPILER) $(FLAGS) `pkg-config --cflags glib-2.0 gstreamer-1.0` $@.c `pkg-config --libs glib-2.0 gstreamer-1.0` -o $@	

relay_stream_with_overlay:
	$(COMPILER) $(FLAGS) $(INCLUDES) $@.c $(LIBS) -o $@

json_rpc_server_test: abstractrpcstubserver.h
	g++ $@.cpp $(FLAGS) -ljsonrpc -o $@

json_rpc_client_test: abstractrpcstubserver.h
	g++ $@.cpp $(FLAGS) -ljsonrpc -o $@

abstractrpcstubserver.h: rpcstubclient.h
	jsonrpcstub -s -o ./ rpc_spec.json RPCSpecStub

rpcstubclient.h: rpc_spec.json
	jsonrpcstub -c -o ./ rpc_spec.json RPCSpecStub

json_rpc_relay: abstractrpcstubserver.h
	$(COMPILER) $(FLAGS) $(INCLUDES) $@.cpp $(LIBS) -ljsonrpc -o $@
