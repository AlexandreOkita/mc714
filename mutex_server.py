import grpc
from concurrent import futures
import time
import test_pb2_grpc as pb2_grpc
import test_pb2 as pb2

class UnaryService(pb2_grpc.UnaryServicer):

    def __init__(self):
        self.locked = False
        self.critical_section = []
    
    def GetServerResponse(self, request, context):
        message = request.message
        if not self.locked:
            print(f"Adding {message} to the critical section")
            self.locked = True
            try:
                time.sleep(10)
                self.critical_section.append(message)
                self.locked = False
                response = f"New critical section: {self.critical_section}"
                added = True
            except Exception as e:
                self.locked = False
                print(f"Exception: {e}")
                response = f"Exception: {e}"
                added = False
        else:
            response = f"Critical section is locked. {message} will not be added to the critical section"
            added = False
        result = {'message': response, 'received': added}
        return pb2.MessageResponse(**result)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_UnaryServicer_to_server(UnaryService(), server)
    server.add_insecure_port('[::]:5000')
    server.start()
    print("Server running")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()