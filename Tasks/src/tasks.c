#include "tasks.h"

#include "main.h"

extern TIM_HandleTypeDef htim2;
extern IWDG_HandleTypeDef hiwdg;

volatile uint32_t tick = 0U;

void Tasks_Init(void)
{
    HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_RESET);

    if (HAL_TIM_Base_Start_IT(&htim2) != HAL_OK)
    {
        Error_Handler();
    }
}

void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim)
{
    if (htim->Instance == TIM2)
    {
        ++tick;
        // (void)HAL_IWDG_Refresh(&hiwdg);
    }
}
