using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;

namespace FishAppUI;

/*
<!-- Image Menu -->
<MenuItem Header="_Image">
    <MenuItem Header="Select Shape">
        <MenuItem Header="Rectangular Selection"    Click="ImageRectangularSelect_Click"/>
        <MenuItem Header="Freeform Selection"       Click="ImageFreeformSelect_Click"/>
        <MenuItem Header="Polygon Selection"        Click="ImagePolygonSelect_Click"/>
    </MenuItem>
    <Separator/>
    <MenuItem Header="Crop"                         Click="ImageCrop_Click"/>
    <MenuItem Header="Resize"                       Click="ImageResize_Click"/>
    <MenuItem Header="Rotate">
        <MenuItem Header="Rotate 90°"               Click="Rotate90Button_Click"/>
        <MenuItem Header="Rotate 180°"              Click="Rotate180Button_Click"/>
        <MenuItem Header="Rotate 270°"              Click="Rotate270Button_Click"/>
    </MenuItem>
    <MenuItem Header="Flip">
        <MenuItem Header="Flip Horizontal"          Click="FlipHorizontal_Click"/>
        <MenuItem Header="Flip Vertical"            Click="FlipVertical_Click"/>
    </MenuItem>
</MenuItem>
 */
public partial class MainWindow
{


    // MenuItem Header = "Rectangular Selection"    Click="ImageRectangularSelect_Click"/>
    public void ImageRectangularSelect_Click(object sender, RoutedEventArgs e) { /* TODO */ }      //Sondre

    // MenuItem Header = "Freeform Selection"       Click="ImageFreeformSelect_Click"/>
    public void ImageFreeformSelect_Click(object sender, RoutedEventArgs e) { /* TODO */ }      //Sondre

    // MenuItem Header = "Polygon Selection"        Click="ImagePolygonSelect_Click"/>
    public void ImagePolygonSelect_Click(object sender, RoutedEventArgs e) { /* TODO */ }      //Sondre


    // MenuItem Header = "Crop"                         Click="ImageCrop_Click"/>
    public void ImageCrop_Click(object sender, RoutedEventArgs e) { /* TODO */ }      //Oscar

    // MenuItem Header = "Resize"                       Click="ImageResize_Click"/>
    public void ImageResize_Click(object sender, RoutedEventArgs e) { /* TODO */ }      //Oscar


    // MenuItem Header = "Rotate 90°"               Click="Rotate90Button_Click"/>
    public async void Rotate90Button_Click(object sender, RoutedEventArgs e) => await ApplyImageOperationAsync("rotate?angle=90");

    // MenuItem Header = "Rotate 180°"              Click="Rotate180Button_Click"/>
    public async void Rotate180Button_Click(object sender, RoutedEventArgs e) => await ApplyImageOperationAsync("rotate?angle=180");

    // <MenuItem Header = "Rotate 270°"              Click="Rotate270Button_Click"/>
    public async void Rotate270Button_Click(object sender, RoutedEventArgs e) => await ApplyImageOperationAsync("rotate?angle=270");



    // < MenuItem Header = "Flip Horizontal"          Click="FlipHorizontal_Click"/>
    public async void FlipHorizontal_Click(object sender, RoutedEventArgs e) => await ApplyImageOperationAsync("flip_horizontal");
    // MenuItem Header = "Flip Vertical"            Click="FlipVertical_Click"/>
    public async void FlipVertical_Click(object sender, RoutedEventArgs e) => await ApplyImageOperationAsync("flip_vertical");



}
