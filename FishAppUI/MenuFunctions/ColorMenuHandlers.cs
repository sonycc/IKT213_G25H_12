using System.Windows;

namespace FishAppUI;


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


public partial class MainWindow
{


    public void ColorPalette_Click(object sender, RoutedEventArgs e)
    {
        OpenColorPalette();
    }


    public void BrushSizeSmall_Click(object sender, RoutedEventArgs e)
    {
        SetBrushSize(BrushSize.Small);
    }

    public void BrushSizeMedium_Click(object sender, RoutedEventArgs e)
    {
        SetBrushSize(BrushSize.Medium);
    }

    public void BrushSizeLarge_Click(object sender, RoutedEventArgs e)
    {
        SetBrushSize(BrushSize.Large);
    }

}
