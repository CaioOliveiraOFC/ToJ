import builtins
import time
import random
from unittest.mock import patch
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

class VictoryException(Exception): pass
class TimeoutException(Exception): pass

class AutoTester:
    """Simula o comportamento de um jogador para testar crashes no fluxo do jogo em background."""
    def __init__(self):
        self.metrics = {
            "actions": 0,
            "combats": 0,
            "crashes": 0,
            "errors": []
        }
        self.current_map = None
        self.patchers = []
        self.player_ref = None
        self.log_buffer = None
        self.last_key = None
        self.consecutive_key_count = 0
        self.position_history = []

    def run_test(self, player):
        import os
        import io
        from datetime import datetime
        from game import start_game
        from toj_source.map import MapOfGame
        from rich.console import Console
        
        self.player_ref = player
        self.log_buffer = io.StringIO()
        self.mock_console = Console(file=self.log_buffer, force_terminal=False, color_system=None)
        real_print = builtins.print
        
        original_draw = MapOfGame.draw_map
        def mocked_draw(map_self):
            self.current_map = map_self
            # Grava o mapa no buffer de log (simulação realista)
            original_draw(map_self)
            return None
            
        def mocked_safe_get_key(valid_keys=None, allow_escape=True):
            self.metrics["actions"] += 1
            
            level = self.player_ref.get_level() if self.player_ref else 1
            
            # Condição de Vitória (Level 20)
            if level >= 20:
                raise VictoryException("Nível 20 atingido!")
                
            # Limite de Ações (Hard Cap de segurança)
            if self.metrics["actions"] > 50000:
                raise TimeoutException("Limite de 50.000 ações atingido (Loop infinito evitado).")
                
            # Verbose ProgressBar
            pct = min(100, int((level / 20) * 100))
            bar_len = 20
            filled = int((pct / 100) * bar_len)
            bar = '=' * filled + '-' * (bar_len - filled)
            real_print(f"\rProgresso Simulação: [{bar}] {pct}% (Lvl {level}/20)", end="", flush=True)
            
            choice = None
            if valid_keys and 'w' in valid_keys and self.current_map:
                choice = self.decide_map_move()
            elif valid_keys and '1' in valid_keys and '4' in valid_keys:
                self.metrics["combats"] += 1
                choice = '1' 
            elif valid_keys and 'x' in valid_keys:
                choice = 'x'
            else:
                choice = valid_keys[0] if valid_keys else 'a'
                
            if choice == self.last_key:
                self.consecutive_key_count += 1
                if self.consecutive_key_count >= 100:
                    raise TimeoutException(f"Stopped because pressed '{choice}' 100 times consecutively (bot is completely stuck).")
            else:
                self.consecutive_key_count = 1
                
            self.last_key = choice
            return choice
            
        def mocked_input(prompt=""): return ""
        def mocked_console_input(console_self, prompt="", **kwargs): return ""
        
        def mocked_print(*args, **kwargs): 
            kwargs['file'] = self.log_buffer
            real_print(*args, **kwargs)
            
        original_console_print = Console.print
        def mocked_console_print(console_self, *args, **kwargs): 
            original_console_print(self.mock_console, *args, **kwargs)
            
        def mocked_sleep(*args, **kwargs): pass

        import toj_source.game_logic
        import toj_source.toj_menu

        self.patchers.extend([
            patch('game.safe_get_key', side_effect=mocked_safe_get_key),
            patch('toj_source.interactions.safe_get_key', side_effect=mocked_safe_get_key),
            patch('builtins.input', side_effect=mocked_input),
            patch('builtins.print', side_effect=mocked_print),
            patch('rich.console.Console.input', side_effect=mocked_console_input, autospec=True),
            patch('rich.console.Console.print', side_effect=mocked_console_print, autospec=True),
            patch('toj_source.map.MapOfGame.draw_map', side_effect=mocked_draw, autospec=True),
            patch('game.sleep', side_effect=mocked_sleep, create=True),
            patch('toj_source.interactions.sleep', side_effect=mocked_sleep, create=True),
            patch('toj_source.game_logic.sleep', side_effect=mocked_sleep, create=True),
            patch('toj_source.toj_menu.sleep', side_effect=mocked_sleep, create=True)
        ])
        
        # Inicia a simulação silenciosa
        real_print("\nIniciando Simulação em Background (Target: Lvl 20)...")
        real_print("O terminal ficará parado, calculando na velocidade máxima...\n")
        
        for p in self.patchers:
            p.start()
        
        try:
            start_game(player)
        except VictoryException:
            pass # Simulação terminou com sucesso!
        except TimeoutException as te:
            self.metrics["errors"].append(f"Última Opção Selecionada: '{self.last_key}'\n{str(te)}")
        except Exception as e:
            import traceback
            self.metrics["crashes"] += 1
            error_msg = f"Última Opção Selecionada: '{self.last_key}'\n{traceback.format_exc()}"
            self.metrics["errors"].append(error_msg)
        finally:
            for p in self.patchers:
                p.stop()
            real_print() # Quebra de linha após a barra de progresso
            self.generate_report(real_print)

    def decide_map_move(self):
        """Inteligência Greedy (gulosa) para achar o inimigo ou saída mais próxima."""
        if not self.current_map: return random.choice(['w', 'a', 's', 'd'])
        py, px = self.current_map.player_pos['y'], self.current_map.player_pos['x']
        
        pos = (py, px)
        self.position_history.append(pos)
        if len(self.position_history) > 100:
            self.position_history.pop(0)
            
        if self.position_history.count(pos) > 20:
            raise TimeoutException(f"Stopped because bot is trapped or oscillating at position {pos}.")
        
        targets = list(self.current_map.enemies_pos.keys())
        if self.current_map.exit_pos:
            targets.append((self.current_map.exit_pos['y'], self.current_map.exit_pos['x']))
            
        if not targets: return random.choice(['w', 'a', 's', 'd'])
            
        closest = min(targets, key=lambda t: abs(t[0]-py) + abs(t[1]-px))
        ty, tx = closest
        
        moves = []
        if ty < py and self.current_map.grid[py-1][px] != '#': moves.append('w')
        if ty > py and self.current_map.grid[py+1][px] != '#': moves.append('s')
        if tx < px and self.current_map.grid[py][px-1] != '#': moves.append('a')
        if tx > px and self.current_map.grid[py][px+1] != '#': moves.append('d')
        
        return random.choice(moves) if moves else random.choice(['w', 'a', 's', 'd'])

    def generate_report(self, real_print):
        import os
        from datetime import datetime
        
        if not os.path.exists("reports"):
            os.makedirs("reports")
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"reports/sim_report_{timestamp}.txt"
        
        final_level = self.player_ref.get_level() if self.player_ref else 0
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write("="*50 + "\n")
            f.write(f"  RELATÓRIO DE SIMULAÇÃO AUTO-TEST  \n")
            f.write("="*50 + "\n")
            f.write(f"Contexto do Agente de Teste:\n")
            f.write(f"- Alvo Principal: Chegar vivo ao Level 20.\n")
            f.write(f"- Limite de Hard Cap: 50.000 ações permitidas.\n")
            f.write(f"- Objetivo: Verificar integridade de código (Crashes) e progressão/balanceamento da XP.\n")
            f.write("-" * 50 + "\n")
            f.write(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Nível Final Alcançado: {final_level}/20\n")
            f.write(f"Ações Simuladas: {self.metrics['actions']}\n")
            f.write(f"Lutas (aprox): {self.metrics['combats']}\n")
            f.write(f"Crashes: {self.metrics['crashes']}\n\n")
            
            if self.metrics["errors"]:
                f.write("="*50 + "\n")
                f.write("  LOG DE ERROS (TRACEBACKS)  \n")
                f.write("="*50 + "\n")
                for err in self.metrics["errors"]:
                    f.write(err + "\n")
            
            f.write("\n" + "="*50 + "\n")
            f.write("  LOG DE INTERFACE CAPTURADO  \n")
            f.write("="*50 + "\n")
            if self.log_buffer:
                f.write(self.log_buffer.getvalue())
                    
        real_print(f"\nSimulação Finalizada!")
        real_print(f"Relatório Completo gerado com sucesso em: {filename}")
        builtins.input("\nPressione Enter para retornar ao menu principal...")
