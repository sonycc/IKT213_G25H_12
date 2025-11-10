using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;

namespace FishAppUI.MenuFunctions
{
    /*

    <!-- Color Menu -->
    <MenuItem Header="_Color">
        <MenuItem Header="Color Palette"    Click="ColorPalette_Click"/>
        <MenuItem Header="Brush Size">
            <MenuItem Header="Small"        Click="BrushSizeSmall_Click"/>
            <MenuItem Header="Medium"       Click="BrushSizeMedium_Click"/>
            <MenuItem Header="Large"        Click="BrushSizeLarge_Click"/>
        </MenuItem>
    </MenuItem>
    */

    public enum BrushSize
    {
        Small,
        Medium,
        Large
    }


    internal class ColorMenuHandlers
    {

        public readonly MainWindow _mainWindow;

        public ColorMenuHandlers(MainWindow mainWindow)
        {
            _mainWindow = mainWindow;
        }

        public void ColorPalette_Click(object sender, RoutedEventArgs e)
        {
            _mainWindow.OpenColorPalette();
        }


        public void BrushSizeSmall_Click(object sender, RoutedEventArgs e)
        {
            _mainWindow.SetBrushSize(BrushSize.Small);
        }

        public void BrushSizeMedium_Click(object sender, RoutedEventArgs e)
        {
            _mainWindow.SetBrushSize(BrushSize.Medium);
        }

        public void BrushSizeLarge_Click(object sender, RoutedEventArgs e)
        {
            _mainWindow.SetBrushSize(BrushSize.Large);
        }

    }


}
