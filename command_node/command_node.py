import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from nav2_msgs.action import NavigateToPose


class CommandNode(Node):

    def __init__(self, posicao_x, posicao_y):

        super().__init__('command_node')
        self.get_logger().info("Nó de comando iniciado.")

        # Posição desejada
        self.posicao_x = posicao_x
        self.posicao_y = posicao_y

        # Cliente da Action do Nav2
        self.action_client = ActionClient(
            self,
            NavigateToPose,
            'navigate_to_pose'
        )

    def enviar_objetivo(self):

        self.get_logger().info("Esperando pelo servidor NavigateToPose...")

        if not self.action_client.wait_for_server(timeout_sec=5.0):
            self.get_logger().error("Servidor NavigateToPose não encontrado!")
            return

        # Criar objetivo
        objetivo = NavigateToPose.Goal()

        objetivo.pose.header.frame_id = 'map'
        objetivo.pose.header.stamp = (self.get_clock().now().to_msg())

        objetivo.pose.pose.position.x = self.posicao_x
        objetivo.pose.pose.position.y = self.posicao_y

        objetivo.pose.pose.orientation.w = 1.0

        self.get_logger().info(
            f"Enviando objetivo: x={self.posicao_x}, y={self.posicao_y}")

        # futuro é um objeto que representa a resposta do Nav2 sobre o objetivo enviado
        futuro = self.action_client.send_goal_async(
            objetivo
        )

        # Esperar o Nav2 responder
        rclpy.spin_until_future_complete(
            self,
            futuro
        )

        # Recuperar o GoalHandle, que é a resposta do Nav2 sobre o objetivo enviado
        objetivo_enviado = futuro.result()

        # Verificar se foi aceito
        if not objetivo_enviado.accepted:
            self.get_logger().error("Objetivo rejeitado pelo Nav2.")
            return

        self.get_logger().info("Objetivo aceito!")

        # Solicitar resultado da navegação
        futuro_resultado = (
            objetivo_enviado.get_result_async()
        )

        # Esperar a navegação terminar
        rclpy.spin_until_future_complete(
            self,
            futuro_resultado
        )

        resultado = futuro_resultado.result()

        self.get_logger().info(
            f"Navegação terminou. Status: {resultado.status}"
        )

def main(args=None):

    rclpy.init(args=args)

    posicao_x = float(input("Digite a posição X do objetivo: "))

    posicao_y = float(input("Digite a posição Y do objetivo: "))
    command_node = CommandNode(posicao_x, posicao_y)

    try:
        command_node.enviar_objetivo()

    except KeyboardInterrupt:
        pass

    command_node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()