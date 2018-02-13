# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

from . import mining_pb2 as mining__pb2


class MiningAPIStub(object):
  # missing associated documentation comment in .proto file
  pass

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.GetBlockMiningCompatible = channel.unary_unary(
        '/qrl.MiningAPI/GetBlockMiningCompatible',
        request_serializer=mining__pb2.GetBlockMiningCompatibleReq.SerializeToString,
        response_deserializer=mining__pb2.GetBlockMiningCompatibleResp.FromString,
        )
    self.GetBlockToMine = channel.unary_unary(
        '/qrl.MiningAPI/GetBlockToMine',
        request_serializer=mining__pb2.GetBlockToMineReq.SerializeToString,
        response_deserializer=mining__pb2.GetBlockToMineResp.FromString,
        )
    self.SubmitMinedBlock = channel.unary_unary(
        '/qrl.MiningAPI/SubmitMinedBlock',
        request_serializer=mining__pb2.SubmitMinedBlockReq.SerializeToString,
        response_deserializer=mining__pb2.SubmitMinedBlockResp.FromString,
        )


class MiningAPIServicer(object):
  # missing associated documentation comment in .proto file
  pass

  def GetBlockMiningCompatible(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def GetBlockToMine(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def SubmitMinedBlock(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_MiningAPIServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'GetBlockMiningCompatible': grpc.unary_unary_rpc_method_handler(
          servicer.GetBlockMiningCompatible,
          request_deserializer=mining__pb2.GetBlockMiningCompatibleReq.FromString,
          response_serializer=mining__pb2.GetBlockMiningCompatibleResp.SerializeToString,
      ),
      'GetBlockToMine': grpc.unary_unary_rpc_method_handler(
          servicer.GetBlockToMine,
          request_deserializer=mining__pb2.GetBlockToMineReq.FromString,
          response_serializer=mining__pb2.GetBlockToMineResp.SerializeToString,
      ),
      'SubmitMinedBlock': grpc.unary_unary_rpc_method_handler(
          servicer.SubmitMinedBlock,
          request_deserializer=mining__pb2.SubmitMinedBlockReq.FromString,
          response_serializer=mining__pb2.SubmitMinedBlockResp.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'qrl.MiningAPI', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))
