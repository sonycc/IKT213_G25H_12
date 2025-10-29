using System;
using System.Windows;

namespace FishAppUI
{
    public partial class NewImageDialog : Window
    {
        public int Width { get; private set; }
        public int Height { get; private set; }
        public string ImageType { get; private set; }

        public NewImageDialog()
        {
            InitializeComponent();
            Width = 800;
            Height = 600;
            ImageType = "PNG";
        }

        private void Preset800x600_Click(object sender, RoutedEventArgs e)
        {
            WidthTextBox.Text = "800";
            HeightTextBox.Text = "600";
        }

        private void Preset1920x1080_Click(object sender, RoutedEventArgs e)
        {
            WidthTextBox.Text = "1920";
            HeightTextBox.Text = "1080";
        }

        private void Preset1024x768_Click(object sender, RoutedEventArgs e)
        {
            WidthTextBox.Text = "1024";
            HeightTextBox.Text = "768";
        }

        private void PresetCustom_Click(object sender, RoutedEventArgs e)
        {
            WidthTextBox.Focus();
        }

        private void OKButton_Click(object sender, RoutedEventArgs e)
        {
            if (int.TryParse(WidthTextBox.Text, out int width) && 
                int.TryParse(HeightTextBox.Text, out int height) &&
                width > 0 && height > 0)
            {
                Width = width;
                Height = height;
                ImageType = ((System.Windows.Controls.ComboBoxItem)ImageTypeComboBox.SelectedItem)?.Content?.ToString() ?? "PNG";
                DialogResult = true;
                Close();
            }
            else
            {
                MessageBox.Show("Please enter valid width and height values (positive integers).", "Invalid Input", MessageBoxButton.OK, MessageBoxImage.Warning);
            }
        }

        private void CancelButton_Click(object sender, RoutedEventArgs e)
        {
            DialogResult = false;
            Close();
        }
    }
}
