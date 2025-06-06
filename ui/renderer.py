"""
游戏渲染模块
"""

import pygame
from models.constants import (
    WHITE, BLACK, RED, GREEN, GRAY, LIGHT_BLUE, GOLD,
    HOME_COLORS, CELL_SIZE, WINDOW_WIDTH, WINDOW_HEIGHT,
    REWARD_COLOR, DISCARD_COLOR
)

class Renderer:
    """游戏渲染类"""
    
    def __init__(self, screen):
        """
        初始化渲染器
        
        Args:
            screen: pygame屏幕对象
        """
        self.screen = screen
        self.init_fonts()
    
    def init_fonts(self):
        """初始化字体"""
        try:
            # 尝试使用系统中文字体
            self.font = pygame.font.Font("C:/Windows/Fonts/simhei.ttf", 20)
            self.big_font = pygame.font.Font("C:/Windows/Fonts/simhei.ttf", 32)
        except:
            try:
                # 备选字体
                self.font = pygame.font.Font("C:/Windows/Fonts/msyh.ttc", 20)
                self.big_font = pygame.font.Font("C:/Windows/Fonts/msyh.ttc", 32)
            except:
                # 如果找不到中文字体，使用系统默认字体
                self.font = pygame.font.SysFont("microsoftyaheimicrosoftyaheiui", 20)
                self.big_font = pygame.font.SysFont("microsoftyaheimicrosoftyaheiui", 32)
    
    def draw_board(self, board):
        """
        绘制游戏棋盘
        
        Args:
            board (Board): 棋盘对象
        """
        self.screen.fill(WHITE)
        
        # 绘制格子
        for i, (x, y) in enumerate(board.cell_positions):
            cell = board.get_cell(i)
            
            # 选择格子颜色
            if cell.is_home_cell():
                color = HOME_COLORS[cell.owner]
            elif cell.is_reward_cell():
                color = REWARD_COLOR
            elif cell.is_penalty_cell():
                color = DISCARD_COLOR
            else:
                color = GRAY
            
            # 绘制格子
            pygame.draw.rect(self.screen, color, 
                           (x - CELL_SIZE//2, y - CELL_SIZE//2, CELL_SIZE, CELL_SIZE))
            pygame.draw.rect(self.screen, BLACK, 
                           (x - CELL_SIZE//2, y - CELL_SIZE//2, CELL_SIZE, CELL_SIZE), 2)
            
            # 显示格子编号
            text = self.font.render(str(i), True, BLACK)
            text_rect = text.get_rect(center=(x, y - 20))
            self.screen.blit(text, text_rect)
            
            # 显示格子类型
            if cell.is_home_cell():
                type_text = f"H{cell.owner + 1}"
            elif cell.is_reward_cell():
                type_text = "奖励"
            elif cell.is_penalty_cell():
                type_text = "丢弃"
            else:
                type_text = "普通"
            
            text = self.font.render(type_text, True, BLACK)
            text_rect = text.get_rect(center=(x, y + 10))
            self.screen.blit(text, text_rect)
    
    def draw_players(self, players, board, animation_manager):
        """
        绘制玩家
        
        Args:
            players (list): 玩家列表
            board (Board): 棋盘对象
            animation_manager (AnimationManager): 动画管理器
        """
        for i, player in enumerate(players):
            # 获取玩家当前位置（可能是动画中的位置）
            if animation_manager.player_moving and animation_manager.moving_player_id == i:
                pos_x, pos_y = animation_manager.get_animated_player_position(i, board)
            else:
                pos_x, pos_y = board.get_cell_position(player.position)
            
            # 为了避免玩家重叠，稍微偏移位置
            offset_x = (i % 2) * 15 - 7
            offset_y = (i // 2) * 15 - 7
            
            # 如果是移动中的玩家，添加发光效果
            if animation_manager.player_moving and animation_manager.moving_player_id == i:
                # 绘制发光效果
                pygame.draw.circle(self.screen, GOLD, 
                                 (pos_x + offset_x, pos_y + offset_y), 12, 2)
            
            pygame.draw.circle(self.screen, player.color, 
                             (pos_x + offset_x, pos_y + offset_y), 8)
            pygame.draw.circle(self.screen, BLACK, 
                             (pos_x + offset_x, pos_y + offset_y), 8, 2)
    
    def draw_ui(self, game_logic):
        """
        绘制用户界面
        
        Args:
            game_logic (GameLogic): 游戏逻辑对象
            
        Returns:
            pygame.Rect: 按钮矩形区域，如果没有按钮则返回None
        """
        # 绘制玩家信息
        y_offset = 10
        for i, player in enumerate(game_logic.players):
            player_type = player.get_player_type_name()
            
            # 检查是否是联机游戏
            is_network_game = hasattr(game_logic, 'is_local_player_turn')
            
            if not player.is_ai:
                # 真人玩家
                from utils.config_manager import config_manager
                if is_network_game and hasattr(player, 'name') and player.name != config_manager.get_nickname():
                    # 联机游戏中的其他玩家，显示他们的昵称
                    text = f"玩家{i + 1}({player.name}): {player.money}金币"
                else:
                    # 本地玩家（单人游戏或联机游戏中的自己），显示配置的昵称
                    text = f"玩家{i + 1}({config_manager.get_nickname()}): {player.money}金币"
            else:
                # AI玩家
                text = f"{player_type}{i + 1}: {player.money}金币"
            
            # 标注本地玩家
            is_local_player = False
            if hasattr(game_logic, 'is_local_player_turn') and hasattr(game_logic, 'player_slot'):
                # 联机游戏：检查是否是本地玩家槽位
                is_local_player = (i == game_logic.player_slot)
            else:
                # 单人游戏：第一个非AI玩家就是本地玩家
                is_local_player = not player.is_ai
            
            if is_local_player:
                text = f"[你] {text}"
            
            if i == game_logic.current_player:
                text = f">>> {text} <<<"
            
            color = BLACK if i != game_logic.current_player else RED
            rendered_text = self.font.render(text, True, color)
            self.screen.blit(rendered_text, (10, y_offset))
            y_offset += 30
        
        # 绘制骰子结果
        if game_logic.dice_result > 0:
            dice_text = f"移动骰子点数: {game_logic.dice_result}"
            rendered_text = self.font.render(dice_text, True, BLACK)
            self.screen.blit(rendered_text, (10, y_offset + 20))
            y_offset += 25
        
        if game_logic.effect_dice_result > 0:
            effect_dice_text = f"效果骰子点数: {game_logic.effect_dice_result}"
            rendered_text = self.font.render(effect_dice_text, True, BLACK)
            self.screen.blit(rendered_text, (10, y_offset + 20))
        
        # 绘制消息
        message_text = self.font.render(game_logic.message, True, BLACK)
        self.screen.blit(message_text, (10, WINDOW_HEIGHT - 80))
        
        # 绘制当前状态提示
        current_player = game_logic.get_current_player()
        
        # 构建当前玩家名称
        if not current_player.is_ai:
            # 真人玩家
            from utils.config_manager import config_manager
            is_network_game = hasattr(game_logic, 'is_local_player_turn')
            
            if is_network_game and hasattr(current_player, 'name') and current_player.name != config_manager.get_nickname():
                # 联机游戏中的其他玩家，显示他们的昵称
                current_player_name = f"玩家{current_player.id + 1}({current_player.name})"
            else:
                # 本地玩家（单人游戏或联机游戏中的自己），显示配置的昵称
                current_player_name = f"玩家{current_player.id + 1}({config_manager.get_nickname()})"
        else:
            # AI玩家
            current_player_name = current_player.get_player_type_name() + str(current_player.id + 1)
        
        if game_logic.waiting_for_effect_dice:
            # 明确显示谁需要投掷效果骰子
            status_text = f"等待 {current_player_name} 投掷效果骰子..."
            status_color = GOLD
        else:
            # 显示当前是谁的回合
            status_text = f"{current_player_name} 的回合"
            status_color = BLACK
        
        status_rendered = self.font.render(status_text, True, status_color)
        status_rect = status_rendered.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT - 40))
        self.screen.blit(status_rendered, status_rect)
        
        # 绘制按钮
        # 判断是否应该显示按钮
        should_show_button = False
        
        # 如果是网络游戏逻辑
        if hasattr(game_logic, 'is_local_player_turn'):
            # 联机游戏：只有本地玩家在自己的回合才能看到按钮
            should_show_button = game_logic.is_local_player_turn()
        else:
            # 单人游戏：当前玩家不是AI就显示按钮
            should_show_button = not current_player.is_ai
        
        if game_logic.is_game_over():
            # 游戏结束时显示重新开始按钮
            button_rect = pygame.Rect(WINDOW_WIDTH - 150, WINDOW_HEIGHT - 60, 120, 40)
            pygame.draw.rect(self.screen, GREEN, button_rect)
            pygame.draw.rect(self.screen, BLACK, button_rect, 2)
            
            button_text = self.font.render("重新开始", True, BLACK)
            text_rect = button_text.get_rect(center=button_rect.center)
            self.screen.blit(button_text, text_rect)
            
            return button_rect
        elif game_logic.waiting_for_effect_dice and should_show_button:
            # 只有本地玩家在自己的回合等待效果骰子时显示投掷按钮
            button_rect = pygame.Rect(WINDOW_WIDTH - 150, WINDOW_HEIGHT - 60, 120, 40)
            pygame.draw.rect(self.screen, GOLD, button_rect)
            pygame.draw.rect(self.screen, BLACK, button_rect, 2)
            
            button_text = self.font.render("投骰子", True, BLACK)
            text_rect = button_text.get_rect(center=button_rect.center)
            self.screen.blit(button_text, text_rect)
            
            return button_rect
        elif should_show_button:
            # 本地玩家回合显示投骰子按钮
            button_rect = pygame.Rect(WINDOW_WIDTH - 150, WINDOW_HEIGHT - 60, 120, 40)
            pygame.draw.rect(self.screen, LIGHT_BLUE, button_rect)
            pygame.draw.rect(self.screen, BLACK, button_rect, 2)
            
            button_text = self.font.render("投骰子", True, BLACK)
            text_rect = button_text.get_rect(center=button_rect.center)
            self.screen.blit(button_text, text_rect)
            
            return button_rect
        
        return None 